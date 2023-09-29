odoo.define('program.BoardView', function(require) {
    'use strict';
    const {patch} = require('web.utils');
    var FormController = require('web.FormController');

    var customBoardController = FormController.extend({
        _saveDashboard: function () {
            debugger;
        }
        }
    )

    var BoardView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: customBoardController,
            Renderer: BoardRenderer,
        }),
    });

    return BoardView;
})




/*
/!** @odoo-module **!/
import { registry } from "@web/core/registry";
import { BoardController } from '@board/board';
import { patch } from "@web/core/utils/patch";

const actionService = registry.category("services").get("action");

// # override the save dashboard default function to add my custom code by using patch method
patch( BoardController, {

    _saveDashboard() {
        console.log("custom save dashboard")
        var board = this.renderer.getBoard();
        var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
        return this._rpc({
            route: '/web/view/edit_custom',
            params: {
                custom_id: this.customViewID ? this.customViewID : " ",
                arch: arch,
            }
        }).then(dataManager.invalidate.bind(dataManager));
    },
});*/



/*
export function customSaveDashboard() {
    // override the save dashboard default function to add this 'this.customViewID ? this.customViewID : ""' to custom_id in params
    // this is to make sure that the custom_id is not empty when saving the dashboard
    Dialog.confirm(this, _t("Are you sure you want to save this dashboard?"), {
        confirm_callback: () => {
            var board = this.renderer.getBoard();
            var arch = QWeb.render('DashBoard.xml', _.extend({}, board));
            return this._rpc({
                route: '/web/view/edit_custom',
                params: {
                    custom_id: this.customViewID,
                    arch: arch,
                }
            }).then(dataManager.invalidate.bind(dataManager));
        }
    });
}
*/

