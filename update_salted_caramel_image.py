import os
import django
import requests
from django.core.files.base import ContentFile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from product.models import Product

def update_salted_caramel_image():
    try:
        # Find the product
        product = Product.objects.filter(name__icontains='salted caramel brownie').first()
        
        if not product:
            print("Salted Caramel Brownie not found!")
            return
        
        # Image URL for salted caramel brownie
        image_url = 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=400'
        
        # Download image
        response = requests.get(image_url)
        if response.status_code == 200:
            image_content = ContentFile(response.content)
            image_name = "salted_caramel_brownie.jpg"
            
            # Save image to product
            product.image.save(image_name, image_content, save=True)
            
            print(f"✅ Successfully updated image for: {product.name}")
            print(f"Image saved as: {product.image.name}")
        else:
            print(f"❌ Failed to download image. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_salted_caramel_image()