odoo.define('pos_numpad_disable.disc_price', function (require) {
    "use strict";

    const components = {
        NumpadWidget: require('point_of_sale.NumpadWidget'),
    };
    const { patch } = require('web.utils');

    patch(components.NumpadWidget, 'pos_controlled_interface', {
            mounted() {
                console.log(this);
                $($('.numpad').find('.mode-button')[2]).addClass('disable');
                $($('.numpad').find('.mode-button')[1]).addClass('disable');
            },
            changeMode(mode) {
                if (mode === 'discount') {
                    return;
                }
                if (mode === 'price') {
                    return;
                }
                this.trigger('set-numpad-mode', { mode });
            }
    });

});