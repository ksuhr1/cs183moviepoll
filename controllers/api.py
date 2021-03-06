# These are the controllers for your ajax api.

# returns the name (first and last) of the user as a string

import gluon.contrib.simplejson
import json
import requests

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
                is_active=r.is_active,
                name=name,
            )
            # returns all movies that belong to this poll 
            movies = db(db.movie.poll_id == r.id).select(db.movie.ALL)
            t['movies'] = movies
            print movies

            polls.append(t)

        else:
            has_more = True
    logged_in = auth.user_id is not None
    return response.json(dict(
        polls=polls,
        logged_in=logged_in,
        has_more=has_more,
    ))


def get_poll():
    q = (db.poll.id == request.vars.poll_id)
    poll = db(q).select().first()

    name = get_name(poll.user_email)

    # movies = (db(db.movie.poll_id == poll.id).select(db.movie.ALL))
    #
    # showtimes = (db(db.showtime.movie_id == request.vars).select(db.showtime.ALL))
    #
    # print(showtimes)
    # print (movies)
    # for r in (movies):
    #     #print(r)
    #     r.showtime = (db(db.showtime.movie_id == r.id).select(db.showtime.ALL))

    t = dict(
        id=poll.id,
        user_email=poll.user_email,
        content=poll.poll_content,
        created_on=poll.created_on,
        updated_on=poll.updated_on,
        is_public=poll.is_public,
        is_active=poll.is_active,
        name=name,
        movies=(db(db.movie.poll_id == poll.id).select(db.movie.ALL)),
    )    
    return response.json(dict(poll=t))


# get showtimes for a given movie
def get_showtimes():
    q = (db.movie.id == request.vars.movie_id)
    movie = db(q).select().first()
    showtimes = (db(db.showtime.movie_id == movie.id).select(db.showtime.ALL))
    return response.json(dict(showtimes=showtimes))


# Note that we need the URL to be signed, as this changes the db.
@auth.requires_signature()
def add_poll():
    
    data = gluon.contrib.simplejson.loads(request.body.read())

    if data['movies']:
        user_email = auth.user.email or None
        p_id = db.poll.insert(poll_content=request.vars.content)
        p = db.poll(p_id)
        
        for movie_item in data['movies']:
            movie_title = movie_item['title']
            m_id = db.movie.insert(poll_id=p_id, title=movie_title, ist_api_id=movie_item['id'])
            for showtime_item in data['showtimes']:
                if showtime_item['movie_id'] == movie_item['id']:
                    db.showtime.insert(movie_id=m_id, ist_api_id=showtime_item['id'])

        name = get_name(p.user_email)
        poll = dict(
            id=p.id,
            user_email=p.user_email,
            content=p.poll_content,
            created_on=p.created_on,
            updated_on=p.updated_on,
            is_public=p.is_public,
            is_active=p.is_active,
            name=name,
            movies=(db(db.movie.poll_id == p_id).select(db.movie.ALL)),
        )

    # supposed to print IP of the requester but not working
    # print current.request.client
    return response.json(dict(poll=poll))


# not used
@auth.requires_signature()
def add_movie():
    # Inserts the track information.
    user_email = auth.user.email or None
    t_id = db.movie.insert(title=request.vars.title)
    t = db.movie(t_id)
    movie = dict(
        id=t.id,
        title=t.title,
    )
    newmovie = db(db.movie.poll_id).select()
    print newmovie


    return response.json(dict(movie=movie))


@auth.requires_signature()
def process_showtimes_vote():
    data = gluon.contrib.simplejson.loads(request.body.read())    
    if data['showtimes']:
        user_email = auth.user.email or None
        
        for r1 in data['showtimes']:
            showtime_id = r1['id']
            q = (db.showtime.id == showtime_id)
            showtime = db(q).select().first()
            
            if showtime is None:
                return "Not Authorized"
            else:
                votes = showtime.votes
                if votes is None:
                    votes = 0
                votes = votes+1
                showtime.update_record(votes=votes)
    return response.json(dict())


@auth.requires_signature()
def toggle_active():
    if auth.user == None:
        return "Not Authorized"

    q = ((db.poll.user_email == auth.user.email) &
         (db.poll.id == request.vars.poll_id))

    poll = db(q).select().first()

    if poll is None:
        return "Not Authorized"
    else:
        if (poll.is_active):
            poll.update_record(is_active=False)
        else:
            poll.update_record(is_active=True)
    # return poll
    return response.json(dict(poll=poll))


############################################################
# remnants
############################################################
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

    return dict()

@auth.requires_signature()
def del_poll():
    if auth.user == None:
        return "Not Authorized"

    q = ((db.poll.user_email == auth.user.email) & (db.poll.id == request.vars.poll_id))
    poll = db(q).delete()
   # poll.delete()

    # q = (db(db.poll.user_email == auth.user.email) & (db.poll.id == request.vars.poll_id))
    # poll = db(q).select().first()
    # if poll is None:
    #     return "Not Authorized"
    # else:
    #     db(db.post.id == request.vars.post_id).delete()
    #     poll.delete()
    return "ok"




############################################################
# international showtimes api calls
############################################################

def search_movies():
    try:
        response_from_api = requests.get(
            url="https://api.internationalshowtimes.com/v4/movies/",
            params={
                "countries": "US",
                "limit": 20,
                "search_query": request.vars.form_title,
                "search_field": "title",
                "min_poster_image_thumbnail_width":"300"
            },
            headers={
                "X-API-Key": "Y8YxMBHwe7EPYnIVnKgPYlznt4Yiap6u",
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        response_content = response_from_api.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.json(dict(
        response_content=response_content,
    ))


def get_one_movie_ist():
    try:
        url_string = "https://api.internationalshowtimes.com/v4/movies/"+request.vars.movie_id
        response_from_api = requests.get(
            url=url_string,
            headers={
                "X-API-Key": "Y8YxMBHwe7EPYnIVnKgPYlznt4Yiap6u",
            },
        )

        response_content = response_from_api.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.json(dict(
        response_content=response_content,
    ))


def get_one_showtime_ist():
    try:
        url_string = "https://api.internationalshowtimes.com/v4/showtimes/"+request.vars.showtime_id
        response_from_api = requests.get(
            url=url_string,
            params={
                "append": "movie,cinema",
            },
            headers={
                "X-API-Key": "Y8YxMBHwe7EPYnIVnKgPYlznt4Yiap6u",
            },
        )

        response_content = response_from_api.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.json(dict(
        response_content=response_content,
    ))


def get_showtimes_ist():
    try:
        response_from_api = requests.get(
            url="https://api.internationalshowtimes.com/v4/showtimes/",
            params={
                "limit": 20,
                "movie_id": request.vars.movie_id,
                "location": request.vars.location,
                "distance": 30,
                "time_from": request.vars.timeFrom,
            },
            headers={
                "X-API-Key": "Y8YxMBHwe7EPYnIVnKgPYlznt4Yiap6u",
            },
        )

        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        response_showtimes = response_from_api.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.json(dict(
        response_showtimes=response_showtimes,
    ))


def get_cities():
    try:
        response_from_api = requests.get(
            url="https://api.internationalshowtimes.com/v4/cities/",
            params={
                "query": request.vars.form_city,

            },
            headers={
                "X-API-Key": "Y8YxMBHwe7EPYnIVnKgPYlznt4Yiap6u",
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        response_city = response_from_api.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.json(dict(
        response_city=response_city,
    ))


def get_cinemas():
    try:
        response_from_api = requests.get(
            url="https://api.internationalshowtimes.com/v4/cinemas/",
            params={
                "location": request.vars.location,
                "limit": 10,
            },
            headers={
                "X-API-Key": "Y8YxMBHwe7EPYnIVnKgPYlznt4Yiap6u",
            },
        )
        # print('Response HTTP Status Code: {status_code}'.format(
        #     status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
        response_cinemas = response_from_api.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

    return response.json(dict(
        response_cinemas=response_cinemas,
    ))



