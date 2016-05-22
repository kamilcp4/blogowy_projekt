picturesCounter = 0
pictures = []

window.loadPicture = ->
    picturesToShow = JSON.parse($('#id_pictures_json').val())
    firstPictureUrl = $('#id_first_picture_url').val()
    $pictureHolder = $('.js-picture-holder')
    for picture in picturesToShow
        title = picture['title']
        url = picture['url']
        isMainPhoto = false
        if url == firstPictureUrl
            isMainPhoto = true
        addPicture(title, url, $pictureHolder, isMainPhoto)


changeTitle = (newTitle, pictureCount) ->
    $picture = $('.js-picture-widget').find("[data-picture-count=#{pictureCount}]")
    url = $picture.attr('src').split('/')
    url = url[url.length-1]
    changePicturesJson(newTitle, url)


deletePicture = (pictureCount) ->
    $picture = $('.js-picture-widget').find("[data-picture-count=#{pictureCount}]")
    console.log($picture)

    # delete form pictures_json
    pictureToDelete = null
    for pict in pictures
        if '/media/' + pict['url'] == $picture.attr('src')
            pictureToDelete = pictures.indexOf(pict)
            break

    $firstPictureUrl = $('#id_first_picture_url')
    if pictures.length > 1
        pictures.splice(pictureToDelete,1)
        if $firstPictureUrl.val() == $picture.attr('src')
            $firstPictureUrl.val('')
    else
        pictures = []
        $firstPictureUrl.val('')

    $('#id_pictures_json').val(JSON.stringify(pictures))

    # delete widget
    $picture.parent().remove()


drag = (ev, pictureCount) ->
    name = $('.js-picture-widget').find("[data-title-picture-count=#{pictureCount}]").val()
    url = $('.js-picture-widget').find("[data-picture-count=#{pictureCount}]").attr('src')
    link = "<img class='mainEntryPicture' alt='#{name}' src='#{url}'>"

    ev.originalEvent.dataTransfer.setData("text", link)


addPicture = (title, url, $pictureHolder, isMainPhoto) ->
    # create picture
    $picture = $("
    <div class='js-picture-widget miniPhotoBox'>
        <a href='#' class='js-close editButton' data-close-picture-count=#{picturesCounter}
            type='button'>Usuń</a>

        <img class='miniPhoto js-picture-drag'
            data-picture-count='#{picturesCounter}'
            src='/media/#{url}' alt='#{title or ''}'
            draggable='true'>

        <div style='clear:both;'></div>

        <input type='checkbox' name='mainPicture'
            #{if isMainPhoto then 'checked' else ''}
            class='js-main-photo-checkbox miniMainCheckbox'
            data-picture-url='#{url}'
            value='mainPicture'>
            <div class='miniMainPhoto'>Zdjęcie główne?</div>

        <div style='clear:both;'></div>

        <input type='text' class='js-change-picture-title miniPhotoTitle'
            data-title-picture-count=#{picturesCounter}
            value='#{title or ''}'>
    </div>")

    if isMainPhoto
        $('#id_first_picture_url').val(url)

    # add to container
    $pictureHolder.append($picture)

    newPicture = {
        url: url,
        title: title or '',
    }

    pictures.push(newPicture)
    $('#id_pictures_json').val(JSON.stringify(pictures))

    # add listeners
    $picture.find('.js-change-picture-title').on('keyup', ->
        changeTitle($(this).val(), $(this).data('title-picture-count')))

    $picture.find('.js-close').on('click', ->
        deletePicture($(this).data('close-picture-count')))

    $picture.find('.js-picture-drag').on('dragstart', (event) ->
        drag(event, $(this).data('picture-count')))

    picturesCounter += 1


sendFile = (file, $pictureHolder) ->
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
                picturesCount = $('.js-main-photo-checkbox').length

                addPicture(title, url, $pictureHolder, not picturesCount)
            else
                alert('Błąd')
        # alert if selected file was too large
        else if xhr.readyState==4 && xhr.status==413
            alert("Wybrany plik jest zbyt duży")
        else if xhr.readyState==4
            alert("Coś poszło nie tak, kod błędu: " + xhr.status)


main = ->
    $(".js-file-upload").on('change', ->
        files = $(this)[0].files
        $pictureHolder = $('.js-picture-holder')

        for file in files
            sendFile(file, $pictureHolder)
    )

    $(".js-show-preview").on('click', ->
        show_preview())

    # bind to js-main-photo-checkbox change event to prevent selecting more
    # than one box
    $(document).on('change', '.js-main-photo-checkbox', null, ->
        if $(".js-picture-holder input:checked").length > 1
            $('.js-main-photo-checkbox').prop('checked', '')
            $(@).prop('checked', 'checked')
            $('#id_first_picture_url').val($(@).data('picture-url'))
        else
            if $(@).prop('checked')
                $('#id_first_picture_url').val($(@).data('picture-url'))
            else
                $('#id_first_picture_url').val('')
    )


changePicturesJson = (newTitle, url) ->
    for picture in pictures
        if picture['url'] == url
            picture['title'] = newTitle

    $('#id_pictures_json').val(JSON.stringify(pictures))


showPreviewText = (markdown_text) ->
    $('.js-markdown-body').hide()

    $('.js-preview').html(markdown_text)
    $('.js-preview').append('<a class="js-edit commentSubmit" href="#">Edytuj</a>')

    $(".js-edit").on('click', ->
        hidePreview())

    $('.js-preview').show()


hidePreview = () ->
    $('.js-preview').hide()
    $('.js-markdown-body').show()

show_preview = () ->
 # create an XHR request
    xhr = new XMLHttpRequest()

    # get form data
    markdown_text = $('.js-markdown-text').val()
    console.log(markdown_text)
    $fd = new FormData()
    $fd.append('markdown_text', markdown_text)

    xhr.open("POST", "/preview")

    csrfToken = $("[name='csrfmiddlewaretoken'").val()
    if csrfToken
        xhr.setRequestHeader('X-CSRFToken', csrfToken)

    xhr.onreadystatechange = ->
        uploadStateChange(xhr)

    # send
    xhr.send($fd)

    uploadStateChange = (xhr) ->
        if xhr.readyState==4
            fileUploadFinish(xhr)

    fileUploadFinish = (xhr) ->
        if xhr.status == 200
            jsonResponse = JSON.parse(xhr.responseText)
            if jsonResponse.info == 'sukces'
                preview_body = jsonResponse.preview_body
                console.log(preview_body)
                showPreviewText(preview_body)
            else
                alert('Błąd')
        # alert if selected file was too large
        else if xhr.readyState==4 && xhr.status==413
            alert("Wybrany plik jest zbyt duży")
        else if xhr.readyState==4
            alert("Coś poszło nie tak, kod błędu: " + xhr.status)


$ ->
    main()
