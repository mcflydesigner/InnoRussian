function handleShowPassButton(field) {
    if($(field).attr('type') === 'password') {
        $(field).attr('type', 'text');
    } else if($(field).attr('type') === 'text') {
        $(field).attr('type', 'password');
    } else {
        throw new EvalError('Unknown type of the field is found. ' +
            'It must be `password` or `text`.')
    }
}