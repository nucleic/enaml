(function ($) {

    function updateSideBarPosition() {

        // If the window width is such that the sidebar will be positioned
        // above the rest of the page content, reset to relative positioning.
        var width = this.$window.width();
        if( width < 992 )
        {
            this.css({
                position: "relative",
                top: 0
            });
            return;
        }

        // Collect the various heights needed for computing position.
        var offset = this.topOffset;
        var height = this.outerHeight(true);
        var winHeight = this.$window.height();
        var parent = this.parent();
        var grandParent = parent.parent();
        var effectiveHeight = Math.max(parent.height(), height);
        var delta = grandParent.height() - effectiveHeight;

        // If the sidebar fits completely on the window, it is fixed in
        // place if less than the effective height, or placed relative
        // top if it is the taller element.
        if( height + offset < winHeight )
        {
            if( delta > 0 )
            {
                this.css({
                    position: "fixed",
                    top: offset
                });
            }
            else
            {
                this.css({
                    position: "relative",
                    top: 0
                });
            }
            return;
        }

        // At this point, the sidebar is taller than the viewport. If it is
        // not the tallest item in the row, scroll it at a rate relative to
        // the scroll percentage of the document. This will cause the sidebar
        // and the taller content to reach the bottom of the scroll at the
        // same time.
        if( delta > 0 )
        {
            var docHeight = $(document).height();
            var scrollTop = this.$window.scrollTop();
            var perc = 1.0 * scrollTop / (docHeight - winHeight);
            this.css({
                position: "relative",
                top: delta * perc
            });
            return;
        }

        // At this point, the sidebar is the tallest item in the row.
        this.css({
            position: "relative",
            top: 0
        });
    }


    $(window).load(function () {
        var sideBar = $("#enamldoc-sidebar");
        var $window = $(window);
        sideBar.$window = $window;
        sideBar.topOffset = $("#navbar").height();
        var updater = $.proxy(updateSideBarPosition, sideBar);
        $window.on("click", updater);
        $window.on("scroll", updater);
        $window.on("resize", updater);
        updater();
    });


    $(document).ready(function () {
        $(".enamldoc-sidenav ul").addClass("nav nav-list");
        $(".enamldoc-sidenav > ul > li > a").addClass("nav-header");
    });

}(window.$jqTheme || window.jQuery));
