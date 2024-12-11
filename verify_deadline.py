from app import create_app, db
from app.models.order import Order

app = create_app()
with app.app_context():
    order = Order.query.get(15)
    print(f"Order #{order.id} deadline: {order.deadline}")
