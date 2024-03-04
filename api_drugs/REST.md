# Django Rest
> [Django REST Framework](https://www.youtube.com/watch?v=i-uvtDKeFgE&list=PLA0M1Bcd0w8xZA3Kl1fYmOH_MfLpiYMRs)
<br>[on git](https://github.com/selfedu-rus/rest-framework)
<br>[Generic views](https://www.django-rest-framework.org/api-guide/generic-views/)
<br>[Serializer relations](https://www.django-rest-framework.org/api-guide/relations/)
<br>[Filtering](http://www.tomchristie.com/rest-framework-2-docs/api-guide/filtering)
```commandline
class Album(models.Model):
    album_name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)

class Track(models.Model):
    album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
    order = models.IntegerField()
    title = models.CharField(max_length=100)
    duration = models.IntegerField()

    class Meta:
        unique_together = ['album', 'order']
        ordering = ['order']

    def __str__(self):
        return '%d: %s' % (self.order, self.title)
```

```commandline
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['order', 'title', 'duration']

class AlbumSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']
```


[Разрешение проблемы с nested relations](https://stackoverflow.com/questions/59732768/django-rest-nested-relationship-is-not-working)

```commandline
class AlbumSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, source='track_set')

    class Meta:
        model = Album
        fields = ['album_name', 'artist', 'tracks']
```

[Если в модели нужно представления по ключи не в виде id](https://stackoverflow.com/questions/47265385/how-can-the-foreign-field-shows-the-name-instead-of-its-id)
```commandline
class AddressRegion(models.Model):
    name = models.CharField(max_length=8)

class AvailableArea(models.Model):
    name = models.CharField(max_length=8)
    addressregion = models.ForeignKey(AddressRegion, default=1, related_name='availableareas', on_delete=models.CASCADE)


class AvailableAreaSerializer(ModelSerializer):
    addressregion_name = serializers.ReadOnlyField(source='addressregion.name')

    class Meta:
        model = AvailableArea
        fields = ('id', 'name', 'addressregion_name')
```
<br>

#### How to filter relationships based on their fields in response using Django REST Framework
[Prefetch](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#django.db.models.Prefetch)
```commandline
from django.db.models import Prefetch

class HouseDetailView(generics.RetrieveAPIView):
  serializer_class = HouseSerializer

  def get_queryset(self):
      return House.objects.prefetch_related(Prefetch('resident_set', queryset=Resident.objects.exclude(car__isnull=True))
```