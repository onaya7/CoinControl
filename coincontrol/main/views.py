from coincontrol.main import main

@main.route('/dashboard', methods=["GET"])
def dashboard():
    pass

@main.route('/expenses', methods=["POST", "GET"])
def expenses():
    pass


