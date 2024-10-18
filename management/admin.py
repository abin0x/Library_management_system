from django.contrib import admin
from .models import Category,Book,IssuedBook


admin.site.register(Category)
from django.contrib import admin
from .models import Author

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name')
    list_filter = ('created_at',)

admin.site.register(Author, AuthorAdmin)


class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'author', 'isbn_number', 'publisher', 'price', 'quantity', 'available', 'cover_image', 'created_at')
    list_editable = ('name', 'category', 'author', 'publisher', 'price', 'quantity', 'available', 'cover_image')
    search_fields = ('name', 'isbn_number', 'publisher')
    list_filter = ('category', 'author', 'available', 'created_at')  # Now valid since created_at is included

class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'due_date', 'return_date')
admin.site.register(Book, BookAdmin)
admin.site.register(IssuedBook,IssuedBookAdmin)