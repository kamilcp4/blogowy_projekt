main = ->
    relatedContainerHeight = $('.mainEntryBox').height() - $('.js-blog-information-container').height()
    $('.js-related-container').height(relatedContainerHeight+40)


$ ->
    main()