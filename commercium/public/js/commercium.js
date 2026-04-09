frappe.ui.form.on('Commercium', {
    refresh: function(frm) {
        // Remove any dismissible intro/alert set from other scripts.
        frm.set_intro('');
        frm.layout.wrapper.find('.form-message-container, .form-message').remove();
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
                callback: function(r) {
                    console.log('connect_to_commercium response:', r);
                    if (r.message && r.message.status === "success") {
                        frappe.msgprint(__('Connected successfully'));

                        // Optional: redirect user
                        if (r.message.redirect_url) {
                            window.location.href = r.message.redirect_url;
                        }
                    }
                }
            });

        }).addClass('btn-primary');
    }
});