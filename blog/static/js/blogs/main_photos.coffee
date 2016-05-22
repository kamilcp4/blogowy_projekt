sendFile = (file, $pictureHolder, $pictureInput) ->
    # create an XHR request
    xhr = new XMLHttpRequest()

    # get form data
    $fd = new FormData()
    $fd.append('file', file)

    xhr.open("POST", "/send_photo")

    csrfToken = $("[name='csrfmiddlewaretoken'").val()
    if csrfToken
        xhr.setRequestHeader('X-CSRFToken', csrfToken)

    xhr.onreadystatechange = ->
        uploadStateChange(xhr, file, $pictureHolder)

    # send
    xhr.send($fd)

    uploadStateChange = (xhr, file, $pictureHolder) ->
        if xhr.readyState==4
            fileUploadFinish(xhr, file, $pictureHolder)

    fileUploadFinish = (xhr, file, $pictureHolder) ->
        if xhr.status == 200
            jsonResponse = JSON.parse(xhr.responseText)
            if jsonResponse.info == 'sukces'
                jsonResponse = JSON.parse(xhr.responseText)
                title = ''
                url = jsonResponse.name
                $pictureHolder.attr('src', "/media/#{url}")
                $pictureInput.val(url)
            else
                alert('Błąd')
        # alert if selected file was too large
        else if xhr.readyState==4 && xhr.status==413
            alert("Wybrany plik jest zbyt duży")
        else if xhr.readyState==4
            alert("Coś poszło nie tak, kod błędu: " + xhr.status)


main = ->
    $(".js-avatar-picture-input").on('change', ->
        file = $(this)[0].files[0]
        $pictureHolder = $('.js-avatar-picture-preview')
        $pictureInput = $('.js-new-avatar-picture-url')

        sendFile(file, $pictureHolder, $pictureInput)
    )

    $(".js-headline-picture-input").on('change', ->
        file = $(this)[0].files[0]
        $pictureHolder = $('.js-headline-picture-preview')
        $pictureInput = $('.js-new-headline-picture-url')

        sendFile(file, $pictureHolder, $pictureInput)
    )

$ ->
    main()
