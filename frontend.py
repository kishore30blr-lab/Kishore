import streamlit as st
import pandas as pd
from backend import Database

# --- Database Connection ---
# IMPORTANT: Replace with your actual database credentials.
# Ensure the database 'performance' exists.
db_params = {
    'dbname': 'performance',
    'user': 'postgres',
    'password': 'your_password', # <-- CHANGE THIS
    'host': 'localhost',
    'port': '5432'
}

# --- App ---
st.set_page_config(page_title="Performance Management System", layout="wide")
st.title("🚀 Performance Management System")

menu = [
    "Employee Profiles",
    "Goal Setting",
    "Task Tracking",
    "Leaderboard",
    "Business Insights",
    "Performance Reporting"
]
choice = st.sidebar.selectbox("Menu", menu)

try:
    with Database(db_params) as db:
        if choice == "Employee Profiles":
            st.subheader("👥 Employee Profiles")
            with st.expander("➕ Add New Employee"):
                with st.form("new_employee_form", clear_on_submit=True):
                    name = st.text_input("Name")
                    email = st.text_input("Email")
                    job_role = st.text_input("Job Role")
                    if st.form_submit_button("Add Employee"):
                        db.create_employee(name, email, job_role)
                        st.success("Employee added successfully!")
            
            employees = db.get_all_employees()
            df_employees = pd.DataFrame(employees, columns=['ID', 'Name', 'Email', 'Job Role'])
            st.dataframe(df_employees, use_container_width=True)

        elif choice == "Goal Setting":
            st.subheader("🎯 Goal Setting")
            employee_list = db.get_all_employees()
            if not employee_list:
                st.warning("Please add employees first.")
            else:
                employee_names = {emp[1]: emp[0] for emp in employee_list}
                selected_employee_name = st.selectbox("Select Employee", list(employee_names.keys()))
                selected_employee_id = employee_names[selected_employee_name]

                with st.expander("🏆 Set New Goal"):
                    with st.form("new_goal_form", clear_on_submit=True):
                        description = st.text_area("Goal Description")
                        target_date = st.date_input("Target Date")
                        status = st.selectbox("Status", ["Draft", "In Progress", "Completed", "Cancelled"])
                        if st.form_submit_button("Set Goal"):
                            db.create_goal(selected_employee_id, description, target_date, status)
                            st.success("Goal set successfully!")

                st.markdown("---")
                st.subheader(f"Goals & Progress for {selected_employee_name}")
                goals = db.get_goals_by_employee(selected_employee_id)
                df_goals = pd.DataFrame(goals, columns=['ID', 'Emp ID', 'Description', 'Target Date', 'Status'])
                
                if df_goals.empty:
                    st.info("No goals set for this employee yet.")
                else:
                    st.dataframe(df_goals, use_container_width=True)
                    for _, row in df_goals.iterrows():
                        st.write(f"**Goal:** {row['Description']}")
                        progress = db.get_goal_progress(row['ID'])
                        st.progress(progress)
                
                st.markdown("---")
                st.subheader("✍️ Provide Feedback")
                if not goals:
                    st.warning("Cannot provide feedback as no goals are set.")
                else:
                    goal_ids = [g[0] for g in goals]
                    selected_goal_id = st.selectbox("Select Goal for Feedback", goal_ids, format_func=lambda x: f"Goal ID: {x}")
                    feedback_text = st.text_area("Feedback")
                    if st.button("Submit Feedback"):
                        db.add_feedback(selected_employee_id, selected_goal_id, feedback_text)
                        st.success("Feedback submitted!")

        elif choice == "Task Tracking":
            st.subheader("✅ Task Tracking")
            employee_list = db.get_all_employees()
            if not employee_list:
                st.warning("Please add employees first.")
            else:
                employee_names = {emp[1]: emp[0] for emp in employee_list}
                selected_employee_name = st.selectbox("Select Employee", list(employee_names.keys()))
                selected_employee_id = employee_names[selected_employee_name]
                
                goals = db.get_goals_by_employee(selected_employee_id)
                if not goals:
                    st.warning(f"{selected_employee_name} has no goals. Please set goals before adding tasks.")
                else:
                    with st.expander("📋 Propose New Task"):
                        with st.form("new_task_form", clear_on_submit=True):
                            description = st.text_area("Task Description")
                            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                            status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
                            outcome = st.text_input("Outcome")
                            date = st.date_input("Date")
                            duration = st.number_input("Duration (hours)", min_value=0.0, step=0.5)
                            goal_map = {g[2]: g[0] for g in goals}
                            selected_goal_desc = st.selectbox("Associated Goal", list(goal_map.keys()))
                            goal_id = goal_map[selected_goal_desc]
                            
                            if st.form_submit_button("Propose Task"):
                                db.create_task(selected_employee_id, description, priority, status, outcome, date, duration, goal_id, approved=False)
                                st.success("Task proposed! Awaiting manager approval.")

                tasks = db.get_tasks_by_employee(selected_employee_id)
                df_tasks = pd.DataFrame(tasks, columns=['ID', 'Emp ID', 'Description', 'Priority', 'Status', 'Outcome', 'Date', 'Duration (hrs)', 'Goal ID', 'Approved'])
                st.dataframe(df_tasks, use_container_width=True)

        elif choice == "Leaderboard":
            st.subheader("🏆 Leaderboard (Completed Tasks)")
            task_counts = db.get_task_counts()
            if not task_counts:
                st.info("No tasks have been completed yet.")
            else:
                df_leaderboard = pd.DataFrame(task_counts, columns=['Employee', 'Tasks Completed'])
                df_leaderboard = df_leaderboard.sort_values(by="Tasks Completed", ascending=False)
                st.dataframe(df_leaderboard, use_container_width=True)

        elif choice == "Business Insights":
            st.subheader("📊 Business Insights")
            st.markdown("### Task Counts per Employee (Completed)")
            task_counts = db.get_task_counts()
            if task_counts:
                df_task_counts = pd.DataFrame(task_counts, columns=['Employee', 'Number of Tasks']).set_index('Employee')
                st.bar_chart(df_task_counts)

            st.markdown("### Total Hours Worked per Employee")
            total_hours = db.get_total_hours()
            if total_hours:
                df_total_hours = pd.DataFrame(total_hours, columns=['Employee', 'Total Hours']).set_index('Employee')
                st.bar_chart(df_total_hours)

        elif choice == "Performance Reporting":
            st.subheader("📑 Performance Reporting")
            employee_list = db.get_all_employees()
            if not employee_list:
                st.warning("No employees found.")
            else:
                employee_names = {emp[1]: emp[0] for emp in employee_list}
                selected_employee_name = st.selectbox("Select Employee", list(employee_names.keys()))
                selected_employee_id = employee_names[selected_employee_name]

                st.markdown("### Goals History")
                goals = db.get_goals_by_employee(selected_employee_id)
                df_goals = pd.DataFrame(goals, columns=['ID', 'Emp ID', 'Description', 'Target Date', 'Status'])
                st.dataframe(df_goals, use_container_width=True)

                st.markdown("### Tasks History")
                tasks = db.get_tasks_by_employee(selected_employee_id)
                df_tasks = pd.DataFrame(tasks, columns=['ID', 'Emp ID', 'Description', 'Priority', 'Status', 'Outcome', 'Date', 'Duration (hrs)', 'Goal ID', 'Approved'])
                st.dataframe(df_tasks, use_container_width=True)

                st.markdown("### Feedback History")
                feedbacks = db.get_feedback_by_employee(selected_employee_id)
                df_feedback = pd.DataFrame(feedbacks, columns=['ID', 'Goal ID', 'Feedback', 'Date'])
                st.dataframe(df_feedback, use_container_width=True)

except psycopg2.OperationalError as e:
    st.error(f"🚨 Database Connection Error: Could not connect to the database. Please check if PostgreSQL is running and your connection details are correct.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
