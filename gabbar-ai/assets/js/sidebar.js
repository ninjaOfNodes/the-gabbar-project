$(function() {
    var $sidebar = $('#sidebar');
    var $overlay = $('#sidebar-overlay');
    var $hamburger = $('#hamburger');
    var $close = $('#sidebar-close');

    function openSidebar() {
        $sidebar.addClass('open');
        $overlay.addClass('active');
    }

    function closeSidebar() {
        $sidebar.removeClass('open');
        $overlay.removeClass('active');
    }

    $hamburger.on('click', openSidebar);
    $close.on('click', closeSidebar);
    $overlay.on('click', closeSidebar);

    // Optionally close sidebar on resize to desktop
    $(window).on('resize', function() {
        if (window.innerWidth > 700) {
            closeSidebar();
        }
    });
});