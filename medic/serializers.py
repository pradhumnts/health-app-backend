from rest_framework import serializers
from .models import Medic, Location, Review, SocialAuthData, Booking

class SocialAuthDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAuthData
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    user_id = serializers.CharField(write_only=True, allow_null=True)
    medic_id = serializers.IntegerField(write_only=True, allow_null=True)

    class Meta:
        model = Review
        depth = 1
        fields = ['id', 'medic', 'user', 'status', 'description', 'user_id',  'medic_id', 'rating', 'tags', 'extra_fields', 'created_at', 'updated_at']

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
    
    def create(self, validated_data):
        # Extract medic_id and user_id from validated data
        medic_id = validated_data.pop('medic_id', None)
        user_id = validated_data.pop('user_id', None)

        # If medic_id is provided, fetch the Medic object
        medic = None
        if medic_id:
            medic = Medic.objects.filter(id=medic_id).first()

        # If user_id is provided, fetch the SocialAuthData object
        social_user = None
        if user_id:
            social_user = SocialAuthData.objects.filter(user_id=user_id).first()

        # Create the Review instance with the provided data
        review = Review.objects.create(medic=medic, social_user=social_user, **validated_data)
        return review
    
    def get_user(self, obj):
        if obj.social_user:
            user = obj.social_user
            picture_url = user.picture if user.picture else None
        elif obj.default_user:
            user = obj.default_user
            picture_url = None
        else:
            user = None
            picture_url = None

        return {
            'id': user.id if user else None,
            'name': user.name if user else None,
            'email': user.email if user else None,
            'picture': picture_url
        }
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'latitude', 'longitude']

class MedicSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    expertise = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()  # Use source to specify the reverse relationship

    class Meta:
        model = Medic
        fields = ['id', 'name', 'picture', 'email', 'phone_number', 'description', 'location', 'verified', 'expertise', 'available', 'area_coverage_km', 'extra_fields', 'created_at', 'updated_at', 'reviews']

    def get_expertise(self, obj):
        return [expertise.name for expertise in obj.expertise.all()]
    
    def get_reviews(self, obj):
        reviews = obj.review_items.filter(status='active')  # Filter only active reviews
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.picture and request:
            representation['picture'] = request.build_absolute_uri(instance.picture.url)
        return representation
    
    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location_instance = Location.objects.create(**location_data)
        
        expertise_data = validated_data.pop('expertise', None)
        
        nurse_instance = Medic.objects.create(location=location_instance, **validated_data)
        
        if expertise_data:
            nurse_instance.expertise.set(expertise_data)
        
        return nurse_instance
    
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        depth = 1