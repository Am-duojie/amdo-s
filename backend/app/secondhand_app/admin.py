from django.contrib import admin
from .models import Category, Product, ProductImage, Order, Message, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'status', 'created_at']
    list_filter = ['status', 'condition', 'category', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ProductImageInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'product', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username', 'product__title']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'product', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'receiver__username', 'content']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__title']
