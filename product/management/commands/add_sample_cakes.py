from django.core.management.base import BaseCommand
from product.models import Product, Category
from django.core.files.base import ContentFile
import requests
from io import BytesIO

class Command(BaseCommand):
    help = 'Add sample cakes to the database'

    def handle(self, *args, **options):
        # Create a default category if it doesn't exist
        category, created = Category.objects.get_or_create(
            name='Cakes',
            defaults={'slug': 'cakes'}
        )
        
        if created:
            self.stdout.write(f'Created category: {category.name}')

        # Sample cake data
        cakes = [
            {
                'name': 'Chocolate Fudge Cake',
                'price': 599.00,
                'description': 'Rich and moist chocolate cake with creamy fudge frosting. Perfect for chocolate lovers.',
                'recipe': 'Ingredients: Dark chocolate, butter, eggs, sugar, flour, cocoa powder. Bake at 350°F for 30 minutes.',
                'image_url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400'
            },
            {
                'name': 'Vanilla Bean Cake',
                'price': 499.00,
                'description': 'Classic vanilla cake made with real vanilla beans and topped with buttercream frosting.',
                'recipe': 'Ingredients: Vanilla beans, butter, eggs, sugar, flour, milk. Bake at 325°F for 25 minutes.',
                'image_url': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=400'
            },
            {
                'name': 'Red Velvet Cake',
                'price': 699.00,
                'description': 'Smooth red velvet cake with cream cheese frosting. A southern classic.',
                'recipe': 'Ingredients: Red food coloring, cocoa powder, buttermilk, cream cheese, butter, sugar, flour.',
                'image_url': 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=400'
            },
            {
                'name': 'Strawberry Shortcake',
                'price': 549.00,
                'description': 'Light sponge cake layered with fresh strawberries and whipped cream.',
                'recipe': 'Ingredients: Fresh strawberries, heavy cream, sponge cake, sugar, vanilla extract.',
                'image_url': 'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400'
            },
            {
                'name': 'Salted Caramel Brownie',
                'price': 649.00,
                'description': 'Decadent chocolate brownie topped with rich salted caramel sauce and a hint of sea salt.',
                'recipe': 'Ingredients: Dark chocolate, butter, eggs, brown sugar, flour, caramel sauce, sea salt. Bake at 350°F for 25 minutes.',
                'image_url': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400'
            }
        ]

        for cake_data in cakes:
            # Check if cake already exists
            if Product.objects.filter(name=cake_data['name']).exists():
                self.stdout.write(f'Cake "{cake_data["name"]}" already exists, skipping...')
                continue

            try:
                # Download image
                response = requests.get(cake_data['image_url'])
                if response.status_code == 200:
                    image_content = ContentFile(response.content)
                    image_name = f"{cake_data['name'].lower().replace(' ', '_')}.jpg"
                    
                    # Create product
                    product = Product.objects.create(
                        category=category,
                        name=cake_data['name'],
                        price=cake_data['price'],
                        description=cake_data['description'],
                        recipe=cake_data['recipe']
                    )
                    
                    # Save image
                    product.image.save(image_name, image_content, save=True)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully added cake: {cake_data["name"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to download image for {cake_data["name"]}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error adding {cake_data["name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Sample cakes added successfully!'))