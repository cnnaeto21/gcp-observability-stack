from locust import HttpUser, task, between
import random

class FlaskUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(5)
    def view_home(self):
        self.client.get("/")
    
    @task(3)
    def view_users(self):
        self.client.get("/users")
    
    @task(2)
    def create_signup(self):
        self.client.post("/signup")
    
    @task(1)
    def view_analytics(self):
        self.client.get("/analytics")
    
    @task(2)
    def view_health(self):
        self.client.get("/health")
