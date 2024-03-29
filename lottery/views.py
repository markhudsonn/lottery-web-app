# IMPORTS
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import make_transient

from app import db, requires_roles
from lottery.forms import DrawForm
from models import Draw, encrypt

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
@login_required
@requires_roles('user')
def lottery():
    return render_template('lottery/lottery.html', name=current_user.firstname)


# view all draws that have not been played
@login_required
@requires_roles('user')
@lottery_blueprint.route('/create_draw', methods=['POST'])
def create_draw():
    form = DrawForm()

    if form.validate_on_submit():
        # sort in ascending order
        sorted_submitted_numbers = sorted([form.number1.data, form.number2.data, form.number3.data,
                                           form.number4.data, form.number5.data, form.number6.data])
        
        # convert to string
        submitted_numbers_string = ' '.join([str(number) for number in sorted_submitted_numbers])

        # encrypt submitted numbers with user's draw key

        # Symmetric
        # submitted_numbers_encrypted = encrypt(submitted_numbers_string, current_user.draw_key)

        # Asymmetric
        submitted_numbers_encrypted = encrypt(submitted_numbers_string, current_user.public_draw_key)

        # create a new draw with the form data.
        new_draw = Draw(user_id=current_user.id, numbers=submitted_numbers_encrypted, master_draw=False,
                        lottery_round=0)
        # add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # re-render lottery.page
        flash('Draw %s submitted.' % submitted_numbers_string)
        return redirect(url_for('lottery.lottery'))

    return render_template('lottery/lottery.html', name=current_user.firstname, form=form)


# view all draws that have not been played
@login_required
@requires_roles('user')
@lottery_blueprint.route('/view_draws', methods=['POST'])
def view_draws():
    # get all draws that have not been played [played=0] by the current user
    playable_draws = Draw.query.filter_by(been_played=False, user_id=current_user.id).all()

    # if playable draws exist
    if len(playable_draws) != 0:
        # decrypt draws
        for draw in playable_draws:
            make_transient(draw)

            # Symmetric
            # draw.view_draw(current_user.draw_key)

            # Asymmetric
            draw.view_draw(current_user.private_draw_key)

        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@login_required
@requires_roles('user')
@lottery_blueprint.route('/check_draws', methods=['POST'])
def check_draws():
    # get played draws by current user, don't need to decrypt as played draws already decrypted
    played_draws = Draw.query.filter_by(been_played=True, user_id=current_user.id).all()

    # if played draws exist
    if len(played_draws) != 0:
        return render_template('lottery/lottery.html', results=played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@login_required
@requires_roles('user')
@lottery_blueprint.route('/play_again', methods=['POST'])
def play_again():
    # Delete played draws by current user
    Draw.query.filter_by(been_played=True, master_draw=False, user_id=current_user.id).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()
