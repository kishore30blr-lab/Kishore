import psycopg2

class Database:
    """A class to handle all database operations for the Performance Management System."""
    def __init__(self, db_params):
        """Initializes the database connection."""
        self.conn = psycopg2.connect(**db_params)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Commits changes and closes the connection."""
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    # --- Employee CRUD ---
    def create_employee(self, name, email, job_role):
        self.cur.execute(
            "INSERT INTO employees (name, email, job_role) VALUES (%s, %s, %s)",
            (name, email, job_role)
        )

    def get_all_employees(self):
        self.cur.execute("SELECT employee_id, name, email, job_role FROM employees")
        return self.cur.fetchall()

    # --- Task CRUD ---
    def create_task(self, employee_id, description, priority, status, outcome, date, duration, goal_id, approved=False):
        """Creates a new task, including the 'approved' status."""
        self.cur.execute(
            """
            INSERT INTO tasks (employee_id, task_description, priority, status, outcome, date, duration_hours, goal_id, approved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (employee_id, description, priority, status, outcome, date, duration, goal_id, approved)
        )

    def get_tasks_by_employee(self, employee_id):
        self.cur.execute("SELECT task_id, employee_id, task_description, priority, status, outcome, date, duration_hours, goal_id, approved FROM tasks WHERE employee_id = %s", (employee_id,))
        return self.cur.fetchall()

    # --- Goal CRUD ---
    def create_goal(self, employee_id, description, target_date, status):
        self.cur.execute(
            "INSERT INTO goals (employee_id, goal_description, target_date, status) VALUES (%s, %s, %s, %s)",
            (employee_id, description, target_date, status)
        )

    def get_goals_by_employee(self, employee_id):
        self.cur.execute("SELECT goal_id, employee_id, goal_description, target_date, status FROM goals WHERE employee_id = %s", (employee_id,))
        return self.cur.fetchall()

    def get_goal_progress(self, goal_id):
        """Calculates goal progress based on the completion of associated tasks."""
        self.cur.execute("SELECT COUNT(*) FROM tasks WHERE goal_id = %s", (goal_id,))
        total_tasks = self.cur.fetchone()[0]
        if total_tasks == 0:
            return 0.0
        self.cur.execute("SELECT COUNT(*) FROM tasks WHERE goal_id = %s AND status = 'Done'", (goal_id,))
        done_tasks = self.cur.fetchone()[0]
        return done_tasks / total_tasks if total_tasks > 0 else 0.0

    # --- Feedback ---
    def add_feedback(self, employee_id, goal_id, feedback_text):
        """Adds feedback for a specific goal and employee."""
        self.cur.execute(
            "INSERT INTO feedback (employee_id, goal_id, feedback_text) VALUES (%s, %s, %s)",
            (employee_id, goal_id, feedback_text)
        )

    def get_feedback_by_employee(self, employee_id):
        """Retrieves all feedback for a given employee."""
        self.cur.execute(
            "SELECT f.feedback_id, f.goal_id, f.feedback_text, f.feedback_date FROM feedback f WHERE f.employee_id = %s ORDER BY f.feedback_date DESC",
            (employee_id,)
        )
        return self.cur.fetchall()

    # --- Business Insights ---
    def get_task_counts(self):
        self.cur.execute(
            """
            SELECT e.name, COUNT(t.task_id)
            FROM employees e
            LEFT JOIN tasks t ON e.employee_id = t.employee_id
            WHERE t.status = 'Done'
            GROUP BY e.name
            """
        )
        return self.cur.fetchall()

    def get_total_hours(self):
        self.cur.execute(
            """
            SELECT e.name, SUM(t.duration_hours)
            FROM employees e
            LEFT JOIN tasks t ON e.employee_id = t.employee_id
            GROUP BY e.name
            """
        )
        return self.cur.fetchall()

    def get_avg_task_duration(self):
        self.cur.execute(
            """
            SELECT e.name, AVG(t.duration_hours)
            FROM employees e
            JOIN tasks t ON e.employee_id = t.employee_id
            GROUP BY e.name
            """
        )
        return self.cur.fetchall()
        
    def get_min_max_task_duration(self):
        self.cur.execute(
            """
            SELECT e.name, MIN(t.duration_hours), MAX(t.duration_hours)
            FROM employees e
            JOIN tasks t ON e.employee_id = t.employee_id
            GROUP BY e.name
            """
        )
        return self.cur.fetchall()
