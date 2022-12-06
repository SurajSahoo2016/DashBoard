#Database Utility Class
import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import streamlit as st
from streamlit_option_menu import option_menu



#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")


if "logged_in" not in st.session_state.keys() or st.session_state["logged_in"] is False:     
    def make_hashes(str_to_hash):
        """
        function to hash a string
        params: str_to_hash (string)
        returns hashed string
        """
        return hashlib.sha256(str.encode(str_to_hash)).hexdigest()

    def check_hashes(hash_to_match,str_to_hash_n_match):
        """
        function to check 2 strings match or not
        params: hash_to_match (string), str_to_hash_n_match(string)
        returns: bool
        """
        if make_hashes(str_to_hash_n_match) == hash_to_match:
            return True
        return False

    choice = st.selectbox("Login or SignUp!",["Login","SignUp"])
    with db.connect() as connection:
        if choice == "Login":
            username = st.text_input(label = "Username", value="")
            password = st.text_input(label = "Password",value = "" ,type="password")
            if st.button("Login!"):
                details = connection.execute(text(
                    f"select username, password from usertable where username = '{username}';"
                ))
                df = pd.DataFrame(details.fetchall(),columns=details.keys())
                actual_pass = df["password"].values[0]
                if check_hashes(actual_pass, password):
                    st.session_state["logged_in"] = True
                    st.write("You are logged in")
                else:
                    st.session_state["logged_in"] = False
                    st.write("You are not logged in")
        elif choice == "SignUp":
            username = st.text_input(label = "Username", value="", key = "username")
            password = st.text_input(label = "Password",value = "" ,type="password", key="password")
            existing_details = connection.execute(text(
                f"select username, password from usertable where username = '{username}';"
            ))
            df = pd.DataFrame(existing_details.fetchall(),columns=existing_details.keys())
            if st.button("SignUp!"):
                if len(df.username) > 0:
                    st.write("Username already exists")
                else:
                    connection.execute(text(
                        f"INSERT INTO usertable (username, password) \
                            VALUES ('{username}','{make_hashes(password)}');"
                        ))
                    st.write("User created")

else:
    with db.connect() as connection:
        select_query_stmnt_year = text( "select year \
                                    from movies\
                                where year is not NULL\
                                group by year \
                                order by year asc;")
        result_yr = connection.execute(select_query_stmnt_year)
        df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
        arr = df.year.values
        option = st.selectbox(
            'select the year you want the find the 10 best movies wrt ratings',
            (arr)
        )
        st.write('You selected:', option)

        year = str(option)

        new_query = "select ge.genre,count(mg.movie_id)\
                    from genres as ge, movie_genres as mg, movies as mo\
                    where ge.genre_id = mg.genre_id and mo.movie_id = mg.movie_id and year= " \
                    + year +  " group by mg.genre_id,ge.genre order by count(mg.movie_id) desc limit 10; "

        result_yr = connection.execute(text(new_query))
        df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())

        st.table(df)

