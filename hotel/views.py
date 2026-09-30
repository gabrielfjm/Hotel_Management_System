from flask import Flask, request, session, redirect, url_for, render_template, flash

from .models import User, db, Rooms, Room_type, Booked, Reservations, Payment
from .forms import PaymentForm, SignUpForm, SignInForm, AboutUserForm, CheckAvailForm, ReserveForm

from hotel import app
import datetime


def _sessao_autenticada():
    # DEF-07: session['user_available'] lança KeyError quando a chave não existe.
    return session.get('user_available', False)


def _periodos_conflitam(entrada_a, saida_a, entrada_b, saida_b):
    # DEF-01: estadias são intervalos [entrada, saída); só há conflito se houver interseção.
    return entrada_a < saida_b and entrada_b < saida_a


def _quartos_ocupados(entrada, saida):
    # DEF-15: cada vínculo de quarto é comparado apenas com a própria reserva (brid == rid).
    vinculos = db.session.query(Booked.room_id, Reservations.checkin_date, Reservations.checkout_date)         .join(Reservations, Booked.brid == Reservations.rid)
    return {quarto for quarto, c1, c2 in vinculos if _periodos_conflitam(entrada, saida, c1, c2)}


def _ler_quartos(texto):
    # DEF-04/05/06: aceita apenas números inteiros de quartos existentes, sem repetição.
    try:
        numeros = [int(parte) for parte in texto.split(",")]
    except ValueError:
        return None
    existentes = {quarto.room_number for quarto in Rooms.query.all()}
    if len(set(numeros)) != len(numeros) or not set(numeros) <= existentes:
        return None
    return numeros


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update/<rid>', methods=('GET', 'POST'))
def update_reservation(rid):
    if session['user_available']:
        cur_res = Reservations.query.get(rid)
        updated_res = ReserveForm(obj=cur_res)
        us = User.query.filter_by(username=session['current_user']).first()
        if request.method == 'POST':
            room_list = updated_res.room_numbers.data.split(",")
            d1 = datetime.datetime.combine(updated_res.checkin_date.data, datetime.time(0, 0))
            d2 = datetime.datetime.combine(updated_res.checkout_date.data, datetime.time(0, 0))
            num = updated_res.num_guests.data

            all_reserves = Reservations.query.all()
            all_bookings = Booked.query.all()
            all_rooms = Rooms.query.all()

            if d2 <= d1 or d1 < datetime.datetime.now() or d2 < datetime.datetime.now():
                flash("Please recheck your date! It has to be at least today! ")
                return redirect(url_for('update_reservation', rid=rid))
            total_num = 0
            for each in room_list:
                for each_reserves in all_reserves:
                    for each_booking in all_bookings:
                        c1 = each_reserves.checkin_date
                        c2 = each_reserves.checkout_date
                        if each_booking.room_id == int(each) and (
                                (c1 <= d1 and d2 <= c2) or (d1 <= c1 and d2 <= c2) or (c1 <= d1 and c2 <= d2) or (
                                d1 <= c1 and c2 <= d2)):
                            flash("The room you are reserving is not available at the time you selected!")
                            return redirect(url_for('update_reservation', rid=rid))
            for each in room_list:
                for each_room in all_rooms:
                    if int(each) == each_room.room_number:
                        total_num += each_room.capacity
            if num > total_num:
                flash(
                    "The rooms you selected can't fit the number of guests you entered. Please restart the reservation!")
                return redirect(url_for('update_reservation', rid=rid))
            cres = Reservations.query.get(rid)
            cres.ruid = us.uid
            cres.checkin_date = updated_res.checkin_date.data
            cres.checkout_date = updated_res.checkout_date.data
            cres.num_guests = updated_res.num_guests.data
            db.session.commit()

            cbooked = Booked.query.filter_by(brid=rid).all()
            for each in cbooked:
                db.session.delete(each)
                db.session.commit()

            for each in room_list:
                single_room = Booked(rid, each)
                db.session.add(single_room)
                db.session.commit()
            return redirect(url_for('show_rooms'))
        return render_template('update.html', updated_res=updated_res)

    flash('You are not a valid user to Edit this Post')
    return redirect(url_for('show_rooms'))


@app.route('/delete/<rid>', methods=('GET', 'POST'))
def delete_reservation(rid):
    if _sessao_autenticada():
        cur_res = Reservations.query.get(rid)
        db.session.delete(cur_res)
        db.session.commit()
        cbooked = Booked.query.filter_by(brid=rid).all()
        for each in cbooked:
            db.session.delete(each)
            db.session.commit()
        return redirect(url_for('show_rooms'))
    flash('You are not a valid user to Delete this Reservation!')
    return redirect(url_for('show_rooms'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signupform = SignUpForm(request.form)
    if request.method == 'POST':
        reg = User(signupform.firstname.data, signupform.lastname.data, \
                   signupform.username.data, signupform.password.data, \
                   signupform.email.data)
        db.session.add(reg)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('signup.html', signupform=signupform)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    signinform = SignInForm()
    if request.method == 'POST':
        em = signinform.email.data
        log = User.query.filter_by(email=em).first()
        if log.password == signinform.password.data:
            current_user = log.username
            session['current_user'] = current_user
            session['user_available'] = True
            return redirect(url_for('show_rooms'))
    return render_template('signin.html', signinform=signinform)


@app.route('/about_user')
def about_user():
    aboutuserform = AboutUserForm()
    if session['user_available']:
        user = User.query.filter_by(username=session['current_user']).first()
        reservations = Reservations.query.filter_by(ruid=user.uid).all()
        payments = Payment.query.filter_by(puid=user.uid).all()
        booked = Booked.query.all()
        return render_template('about_user.html', user=user, reservations=reservations, booked=booked,
                               payments=payments,
                               aboutuserform=aboutuserform)
    flash('You are not a Authenticated User')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    session['user_available'] = False
    return redirect(url_for('index'))

global_avail = None

@app.route('/rooms')
def show_rooms():
    if _sessao_autenticada():
        all_rooms = Rooms.query.all()
        all_room_type = Room_type.query.all()
        global global_avail
        if global_avail is None:
            return render_template('rooms.html', rooms=all_rooms, room_type=all_room_type)
        # If entered information on check availability page, only display rooms available at that point
        c_in = datetime.datetime.combine(global_avail.checkin_date.data, datetime.time(0, 0))
        c_out = datetime.datetime.combine(global_avail.checkout_date.data, datetime.time(0, 0))
        ocupados = _quartos_ocupados(c_in, c_out)
        for each in all_rooms:
            if each.room_number in ocupados and (c_in < c_out):
                all_rooms.remove(each)
        global_avail = None
        return render_template('rooms.html', rooms=all_rooms, room_type=all_room_type)
    flash('User is not Authenticated')
    return redirect(url_for('index'))


@app.route('/available', methods=['GET', 'POST'])
def check_available():
    if _sessao_autenticada():
        reservation = CheckAvailForm(request.form)
        us = User.query.filter_by(username=session['current_user']).first()
        if request.method == 'POST':
            global global_avail
            global_avail = reservation
            return redirect(url_for('show_rooms'))
        return render_template('add_room.html', reservation=reservation)
    flash('User is not Authenticated')
    return redirect(url_for('index'))


@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if _sessao_autenticada():
        reservation = ReserveForm(request.form)
        us = User.query.filter_by(username=session['current_user']).first()
        if request.method == 'POST':
            room_list = _ler_quartos(reservation.room_numbers.data)
            num = reservation.num_guests.data
            checkin = reservation.checkin_date.data
            checkout = reservation.checkout_date.data
            # DEF-03/18/19: dados malformados ou menos de um hóspede são rejeitados antes de gravar.
            if room_list is None or num is None or num < 1 or checkin is None or checkout is None:
                flash("Please recheck the room numbers, the number of guests and the dates!")
                return redirect(url_for('reserve'))
            d1 = datetime.datetime.combine(checkin, datetime.time(0, 0))
            d2 = datetime.datetime.combine(checkout, datetime.time(0, 0))

            # DEF-02: comparar a data de entrada com a data de hoje, e não com o instante atual.
            if d2 <= d1 or d1.date() < datetime.date.today():
                flash("Please recheck your date! It has to be at least today! ")
                return redirect(url_for('reserve'))
            total_num = 0
            ocupados = _quartos_ocupados(d1, d2)
            for each in room_list:
                if each in ocupados:
                    flash("The room you are reserving is not available at the time you selected!")
                    return redirect(url_for('reserve'))
            for each_room in Rooms.query.all():
                if each_room.room_number in room_list:
                    total_num += each_room.capacity
            if num > total_num:
                flash(
                    "The rooms you selected can't fit the number of guests you entered. Please restart the reservation!")
                return redirect(url_for('reserve'))
            # Reserva, vínculos e custo gravados em uma única transação; flush() obtém o rid.
            reserve = Reservations(us.uid, checkin, checkout, num, 0)
            db.session.add(reserve)
            db.session.flush()
            # Storing each rooms booked into the Booked table along with reservation id
            for each in room_list:
                db.session.add(Booked(reserve.rid, each))
            reserve.costs = cal_cost(reserve.rid)
            db.session.commit()
            return redirect(url_for('show_rooms'))
        return render_template('reservation.html', reservation=reservation)
    flash("User Not Authenticated !")
    return redirect(url_for('index'))


def cal_cost(rid):
    booked_room_list = Booked.query.filter_by(brid=rid).all()
    room_list = Rooms.query.all()
    cost_daily = 0
    for each in booked_room_list:
        each_room_id = each.room_id
        for e in room_list:
            if each_room_id == e.room_number:
                cost_daily += e.cost
    cur_res = Reservations.query.get(rid)
    checkin = cur_res.checkin_date
    checkout = cur_res.checkout_date
    dateRange = (checkout - checkin).days
    total_cost = cost_daily * dateRange
    return total_cost


@app.route('/payment/<rid>', methods=['GET', 'POST'])
def payment(rid):
    if session['user_available']:
        payment = PaymentForm(request.form)
        us = User.query.filter_by(username=session['current_user']).first()
        if request.method == "POST":
            pd = Payment(us.uid, rid, payment.cardname.data, payment.cardnumber.data, "Confirmed")
            db.session.add(pd)
            db.session.commit()
            return redirect(url_for('show_rooms'))
    return render_template('payment.html', payment=payment)


if __name__ == '__main__':
    app.run()
