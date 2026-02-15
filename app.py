import streamlit as st
import os
from minisql.catalog.table_manager import TableManager
from minisql.index.index_manager import IndexManager
from minisql.query.executer import QueryExecutor
from minisql.query.tokenizer import Tokenizer
from minisql.query.parser import Parser

st.set_page_config(page_title="MiniSQL Database Engine", layout="wide")
st.title("MiniSQL Management System")

DB_PATH = r"C:\Users\poudy\Downloads\DSA\data\data.db"

if "tm" not in st.session_state:
    st.session_state.tm = TableManager(db_path=DB_PATH)

if "im" not in st.session_state:
    st.session_state.im = IndexManager()

if "executor" not in st.session_state:
    st.session_state.executor = QueryExecutor(st.session_state.tm, st.session_state.im)

with st.sidebar:
    st.header("Database Metadata")
    
    if os.path.exists(DB_PATH):
        st.caption(f"Connected to: {DB_PATH}")
    
    tables = st.session_state.tm.list_tables()
    if tables:
        for table_name in tables:
            schema = st.session_state.tm.get_table_schema(table_name)
            rows = getattr(schema, 'data', [])
            st.write(f"**Table:** `{table_name}` ({len(rows)} rows)")
            with st.expander("Columns"):
                for col in schema.columns:
                    pk = " (PK)" if col.primary_key else ""
                    st.text(f"- {col.name}: {col.type}{pk}")
    else:
        st.info("No tables found in data.db")
    
    st.divider()
    if st.button("Force Refresh UI"):
        st.rerun()

query = st.text_area("SQL Query Editor:", height=150, placeholder="Enter your SQL query here")
if st.button("Run Query"):
    if query.strip():
        try:
            tokens = Tokenizer(query).tokenize()
            ast = Parser(tokens).parse()
            result = st.session_state.executor.execute(ast)
            
            st.subheader("Query Result")
            if isinstance(result, list):
                if result:
                    st.table(result)
                else:
                    st.warning("Empty set.")
            else:
                st.success(result)
                st.rerun()
                
        except Exception as e:
            st.error(f"Execution Error: {e}")
    else:
        st.warning("Please enter a query first.")
        
        st.info("Hint: Try entering a SQL query like 'SELECT * FROM users' or 'INSERT INTO users (name, age) VALUES (\"Alice\", 30)'.")