/*
    Class to handle clicks on cards.
    Using AJAX handle adding to favourites / removing from favourites cards.
 */

class CardClickHandler {
    constructor({
                    element, image_add, image_del,
                    image_star, callBack=null,
                    nameOfCookieCsrf = 'csrftoken'
                } = {}) {
        this._elem = element;
        this._callBackFunc = callBack;
        this.image_add = image_add;
        this.image_del = image_del;
        this.image_star = image_star;
        this._csrfToken = this._getCsrfToken(nameOfCookieCsrf);
        this._setupAjax(this._csrfToken);
        this._handleClick = this._handleClick.bind(this);

        $(this._elem).on('click', this._handleClick);
    }

    _handleClick(event) {
        let target = event.target;
        let targetParent = $(event.target).parent();

        if (target.tagName != 'IMG' ||
            !targetParent.hasClass('favourite_button')) return;

        $(this._elem).off('click');

        let action = targetParent.attr('data-action');
        let cardUrl = targetParent.attr('data-url');
        target = $(target); //convert for jQuery
        let newUrl = null;
        let itemElement = null;

        switch (action) {
            case 'del':
                this._removeCardFromFavourite(cardUrl);

                targetParent.attr('data-action', 'add');

                newUrl = cardUrl.replace('/del/', '/add/');
                targetParent.attr('data-url', newUrl);

                target.attr('src', this.image_add);

                itemElement = targetParent;

                //Iterate until reach div element with class 'item'
                while (true) {
                    itemElement = itemElement.parent();

                    if (itemElement.hasClass('item')) break;
                }


                let star_img = itemElement.find('.star_img');

                $(star_img).hide('slow', function(){
                    star_img.remove();
                    itemElement.removeClass('border-gold');
                    this._callBack(action);
                }.bind(this));

                break;

            case 'del-only':
                this._removeCardFromFavourite(cardUrl);

                itemElement = targetParent;

                //Iterate until reach div element with class 'item'
                while (true) {
                    itemElement = itemElement.parent();

                    if (itemElement.hasClass('item')) break;
                }

                $(itemElement).hide('slow', function(){
                    itemElement.remove();
                    this._callBack(action);
                }.bind(this));
                break;


            case 'add':
                this._addCardToFavourite(cardUrl);
                targetParent.attr('data-action', 'del');

                newUrl = cardUrl.replace('/add/', '/del/');
                targetParent.attr('data-url', newUrl);

                target.attr('src', this.image_del);

                itemElement = targetParent;

                while (true) {
                    itemElement = itemElement.parent();

                    if (itemElement.hasClass('item')) break;
                }

                itemElement.addClass('border-gold');
                itemElement.find('.left-part').prepend(
                    '<div class="star_img">' +
                        '<img class="star"' +
                        'src="' + this.image_star + '" ' +
                        'alt="Star image">' +
                    '</div>');
                break;
        }

        $(this._elem).on('click', this._handleClick);
    }

    _addCardToFavourite(cardUrl) {
        let data = {};

        this._sendRequestToServer(cardUrl, data);
    }

    _callBack(action) {
        if(this._callBackFunc) {
            this._callBackFunc(action);
        }
    }

    _removeCardFromFavourite(cardUrl) {
        let data = {};

        this._sendRequestToServer(cardUrl, data, 'DELETE');
    }

    // Send AJAX request to the server
    _sendRequestToServer(url, data, type = 'POST') {
        $.ajax({
            dataType: 'json',
            type: type,
            url: url,
            data: data,
            statusCode: {
                // Data on the page is old
                409: function (response) {
                    alert(response.responseJSON.error + 'The page is reloading :)');
                    window.location.reload();
                },
                410: function (response) {
                    alert(response.responseJSON.error + 'The page is reloading :)');
                    window.location.reload();
                }
            }
        });
    }

    // Setup CSRF token for future AJAX requests
    _setupAjax(csrftoken) {
        // Function to set Request Header with `CSRFTOKEN`
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }

    _csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // Implement CSRF protection
    _getCsrfToken(nameOfCookie) {
        // Function to GET csrftoken from Cookie
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, nameOfCookie.length + 1) === (nameOfCookie + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(nameOfCookie.length + 1));
                    break;
                }
            }
        }

        if (!cookieValue) {
            throw new Error('Cookie `' + nameOfCookie + '` not found!');
        }

        return cookieValue;
    }
}