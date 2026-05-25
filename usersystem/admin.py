
# ================= SITE SETTINGS =================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    list_display = (
        'site_logo',
    )