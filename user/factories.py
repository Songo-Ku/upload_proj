import factory
from factory import fuzzy  # this line is required from some technical reasons
from user.models import User



class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%d' % n)
    plan = factory.fuzzy.FuzzyChoice(['Enterprise', 'Premium', 'Basic'])