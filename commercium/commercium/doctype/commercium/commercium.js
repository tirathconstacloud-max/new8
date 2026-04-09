frappe.ui.form.on('Commercium', {
    refresh: function(frm) {
        frm.disable_save();
        if (frm.page && frm.page.btn_primary) {
            frm.page.btn_primary.hide();
        }
        if (frm.page && frm.page.btn_secondary) {
            frm.page.btn_secondary.hide();
        }

        frm.dashboard.clear_headline();
        frm.layout.wrapper.find('.commercium-config-intro').remove();
        $(`
            <div class="commercium-config-intro" style="margin-bottom: 16px;">
                <div style="font-size: 15px; font-weight: 700; color: var(--text-color);">
                    ${__('Connect to Commercium')}
                </div>
                <p class="text-muted small" style="margin: 6px 0 0 0;">
                    ${__('Click "Connect to Commercium" to securely integrate your ERP with Commercium platform using OAuth authentication.')}
                </p>
            </div>
        `).prependTo(frm.layout.wrapper);
        

        frm.add_custom_button(__('Connect to Commercium'), function() {
            const payload = {
                method: 'commercium.api.connect_to_commercium',
                args: {}
            };

            console.log('Calling Commercium connect_to_commercium with payload:', payload);

            frappe.call({
                method: payload.method,
                args: payload.args,
                freeze: true,
                freeze_message: __('Connecting...'),
                callback: function(r) {
                    console.log('connect_to_commercium response:', r);
                    if (r.message && r.message.status === "success") {
                        frappe.msgprint(__('Successfully Connected!'));
                        if (r.message.redirect_url) {
                            window.location.href = r.message.redirect_url;
                        }
                    } else if (!r.exc) {
                        frappe.msgprint(__('Successfully Connected!'));
                    }
                }
            });
        }).addClass('btn-primary');
    }
});