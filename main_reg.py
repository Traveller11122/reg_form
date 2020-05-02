from flask import Flask, render_template, redirect
from data import db_session
from data.users import User
from data.jobs import Jobs
from data.LoginForm import LoginForm
from data.JobsForm import JobForm
from flask_login import LoginManager, login_user, logout_user, login_required
from data.register import RegisterForm
from data.jobs_api import blueprint
from flask import make_response, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/mars_explorer.sqlite")
    app.register_blueprint(blueprint)
    app.config['JSON_AS_ASCII'] = False

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.route("/")
    def index():
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        users = session.query(User).all()
        names = {name.id: (name.surname, name.name) for name in users}
        return render_template("index.html", jobs=jobs, names=names, title="Work Status")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Пароли не совпадают")
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
                surname=form.surname.data,
                age=form.age.data,
                speciality=form.speciality.data,
                position=form.position.data,
                address=form.address.data,
                # about=form.about.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route('/addjob', methods=['GET', 'POST'])
    def add_job():
        session = db_session.create_session()
        form = JobForm()
        if form.validate_on_submit():
            job = Jobs(
                team_leader=form.team_leader.data,
                job=form.job.data,
                work_size=form.work_size.data,
                is_finished=form.is_finished.data,
                collaborators=form.collaborators.data
                # about=form.about.data
            )
            session.add(job)
            session.commit()
            return redirect('/')
        return render_template('addjob.html', title='Добавление работы', form=form)

    @login_manager.user_loader
    def load_user(user_id):
        session = db_session.create_session()
        return session.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    app.run()


if __name__ == '__main__':
    main()
