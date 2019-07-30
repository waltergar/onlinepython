from app import app
from flask import Flask, flash, render_template

@app.route('/index')
def student():
    return render_template('admin.html')
