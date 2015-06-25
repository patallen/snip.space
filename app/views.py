from app import app, db, login_manager
from app.forms import SnippetForm, SignupForm, LoginForm, DeleteForm, ChangePasswordForm, PreferencesForm, RequestResetForm, PasswordResetForm
from app.models import Snippet, User, Language
from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, abort
from flask import Response, make_response, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from util.email import generateToken, decodeToken, sendEmail
from util.getters import getSnippetByUuid, getUserByUsername
from util.helpers import populateChoiceField
from util.errors import Unauthorized
from util.decorators import anonymous_required