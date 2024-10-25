odoo.define('blog_post.product_template_short_description', function (require) {
    "use strict";

    var core = require('web.core');
    var BasicView = require('web.BasicView');
    var _t = core._t;

    BasicView.include({
        renderElement: function () {
            this._super.apply(this, arguments);
            if (this.$el.find('.o_field_char[name="short_description"]').length) {
                this.$el.find('.o_field_char[name="short_description"]').on('input', function (event) {
                    var maxLength = 100;
                    var currentLength = $(this).val().length;
                    if (currentLength > maxLength) {
                        $(this).val($(this).val().substring(0, maxLength));
                    }
                });
            }
        },
    });
});