from coincontrol.main import main

@main.route('/dashboard', methods=["GET"])
def dashboard():
    pass
@main.route('/incomes', methods=["POST", "GET"])
def  income():
    pass
@main.route('/expenses', methods=["POST", "GET"])
def expenses():
    pass

@main.route('/budgets', methods=["POST", "GET"])
def budgets():
    pass

@main.route('/savings', methods=["POST", "GET"])
def  savings():
    pass

@main.route('/profile', methods=["GET", "PUT"])
def  profile():
    pass

@main.route('/reports/expenses', methods=["GET"])
def  reports_expenses():
    pass

@main.route('/reports/budgets', methods=["GET"])
def  reports_budgets():
    pass

@main.route('/reports/savings', methods=["GET"])
def  reports_savings():
    pass

