(function ($) {

    function updateSideBarPosition() {

        // If the window width is such that the sidebar will be stacked
        // on top, reset the relative top offset to zero.
        var width = this.$window.width();
        if( width < 992 )
        {
            this.css("top", 0);
            return;
        }

        // If the sidebar fits completely on the window, pin the top of
        // the bar to the scroll position, "fixing" it in-place.
        var offset = this.topOffset;
        var height = this.outerHeight(true);
        var winHeight = this.$window.height();
        var scrollTop = this.$window.scrollTop();
        if( height + offset < winHeight )
        {
            this.css("top", scrollTop);
            return;
        }

        // The sidebar is taller than the viewport. If it is not the
        // tallest item in the row, scroll it at a rate relative to
        // the scroll percentage of the document. This will cause the
        // sidebar and the taller content to reach the bottom of the
        // scroll at the same time, but with different scroll rates.
        var parent = this.parent();
        var grandParent = this.parent().parent();
        var effectiveHeight = Math.max(parent.height(), height);
        var delta = grandParent.height() - effectiveHeight;
        if( delta > 0 )
        {
            var docHeight = $(document).height();
            var perc = 1.0 * scrollTop / (docHeight - winHeight);
            this.css("top", delta * perc);
            return;
        }

        // The sidebar is the tallest item in the row, treat it normally.
        this.css("top", 0);
    }


    $(window).load(function () {
        var sideBar = $("#enamldoc-sidebar");
        if( sideBar.length )
        {
            var $window = $(window);
            sideBar.$window = $window;
            sideBar.topOffset = sideBar.offset().top;
            var updater = $.proxy(updateSideBarPosition, sideBar);
            $window.on('click', updater);
            $window.on('scroll', updater);
            $window.on('resize', updater);
            updater();
        }
    });


    $(document).ready(function () {
        $(".enamldoc-sidenav ul").addClass("nav nav-list");
        $(".enamldoc-sidenav > ul > li > a").addClass("nav-header");
    });

}(window.$jqTheme || window.jQuery));
