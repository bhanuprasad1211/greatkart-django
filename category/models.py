from django.db import models
from django.urls import reverse
# Create your models here.

class Category(models.Model) :
    category_name=models.CharField(max_length=150,unique=True)
    slug=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True)
    cat_img=models.ImageField(upload_to='photos/category',blank=True)
    def __str__(self):
        return self.category_name
    class Meta :
        verbose_name='category'
        verbose_name_plural='categories'
    def get_url(self) :
            return reverse('products_by_category',args=[self.slug])
