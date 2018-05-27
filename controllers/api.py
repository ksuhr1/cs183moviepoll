# These are the controllers for your ajax api.

# returns the name (first and last) of the user as a string 
def get_name(email):
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def get_polls():
    start_idx = int(request.vars.start_idx) if request.vars.start_idx is not None else 0
    end_idx = int(request.vars.end_idx) if request.vars.end_idx is not None else 0

    polls = []
    has_more = False

    if auth.user is not None:
        q = db((db.poll.user_email == auth.user.email) | (db.poll.is_public == True))
        rows = q.select(db.poll.ALL, orderby=~db.poll.created_on, limitby=(start_idx, end_idx + 1))
    else:         
        q = db(db.poll.is_public == True)
        rows = q.select(db.poll.ALL, orderby=~db.poll.created_on, limitby=(start_idx, end_idx + 1))

    for i, r in enumerate(rows):
        name = get_name(r.user_email)
        if i < end_idx - start_idx:
            t = dict(
                id=r.id,
                user_email=r.user_email,
                content=r.poll_content,
                created_on=r.created_on,
                updated_on=r.updated_on,
                is_public=r.is_public,
                name=name,
            )

            # returns all movies that belong to this poll 
            movies = db(db.movie.poll_id == r.id).select(db.movie.ALL)
            t['movies'] = movies
            polls.append(t)
        else:
            has_more = True
    logged_in = auth.user_id is not None
    return response.json(dict(
        polls=polls,
        logged_in=logged_in,
        has_more=has_more,
    ))


# Note that we need the URL to be signed, as this changes the db.
@auth.requires_signature()
def add_poll():
    user_email = auth.user.email or None
    p_id = db.poll.insert(poll_content=request.vars.content)
    p = db.poll(p_id)
    name = get_name(p.user_email)
    poll = dict(
            id=p.id,
            user_email=p.user_email,
            content=p.poll_content,
            created_on=p.created_on,
            updated_on=p.updated_on,
            is_public=p.is_public,
            name=name,
    )
    return response.json(dict(poll=poll))


@auth.requires_signature()
def toggle_public():
    if auth.user == None:
        return "Not Authorized"

    q = ((db.poll.user_email == auth.user.email) &
         (db.poll.id == request.vars.poll_id))

    poll = db(q).select().first()

    if poll is None:
        return "Not Authorized"
    else:
        if (poll.is_public):
            poll.update_record(is_public=False)
        else:
            poll.update_record(is_public=True)
    # return poll
    return response.json(dict(poll=poll))

@auth.requires_signature()
def edit_poll():
    poll = db(db.poll.id == request.vars.id).select().first()
    poll.update_record(poll_content=request.vars.poll_content)

    print poll
    return dict()


@auth.requires_signature()
def del_poll():
    """Used to delete a poll."""
    # Implement me!
    db(db.poll.id == request.vars.poll_id).delete()
    return "ok"
