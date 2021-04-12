/*
    Handling form for local / global search based on the value of radio button.
*/

class SearchForm {
    constructor(formId, urlGlobal, _switchFieldId='where-to-search') {
        this.formId = formId;
        this.urlGlobal = urlGlobal;
        this._switchFieldId = _switchFieldId;
        $('#' + formId).submit(this._handleForm.bind(this));
    }

    _handleForm(e) {
        //e.preventDefault();
        let fields = null;
        $('#' + this.formId).each(function () {
            fields = $(this).find(':input:not(:submit)');
        });

        if (!fields) {
            throw new Error('No fields found.');
        }

        let globalSearchFlag = this._isGlobal(fields);

        if(globalSearchFlag) {
            //So, we need to do a global search
            this._redirectToGlobalSearch();
        } else {
            //So, we need to do a local search
            this._redirectToLocalSearch();
        }

    }

    _isGlobal(fields) {
        let result = null;

        fields.each(function (data) {
            if ($(this).is('[id]') &&
            $(this).attr('id').localeCompare(this._switchFieldId)) {
                result = $(this).is(':checked') ? 1 : 0;
            }
        });

        if(result === null) {
            throw new Error("Couldn't find field `search-type`");
        }

        return result;
    }

    _redirectToGlobalSearch(url) {
        $('#' + this.formId).attr('action', this.urlGlobal);
    }

    _redirectToLocalSearch(url) {
        $('#' + this.formId).attr('action', "#");
    }
}