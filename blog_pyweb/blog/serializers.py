from datetime import datetime
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tablo, Comment


class AuthorSerializer(serializers.ModelSerializer):
    """ Автор статьи """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined')


class TablosSerializer(serializers.ModelSerializer):
    """ Статьи для блога """

    # Меняем вывод, вместо `ID` пользователя будет `Имя`
    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    average_rating = serializers.DecimalField(max_digits=6, decimal_places=5)

    class Meta:
        model = Tablo
        fields = ['id', 'title', 'message', 'date_add', 'author', 'average_rating', ]  # добавить 'average_rating', после включения в 19 строке


class CommentsSerializer(serializers.ModelSerializer):
    """ Комментарии и оценки. Используется в методе: `/note/{note_id}/` Статя блога """
    author = AuthorSerializer(read_only=True)

    # Меняем название параметра в ответе
    comment_id = serializers.SerializerMethodField('get_comment_id')
    def get_comment_id(self, obj):
        return obj.pk

    # Переопределяем параметр в ответе
    rating = serializers.SerializerMethodField('get_rating')
    def get_rating(self, obj):
        return {
            'value': obj.rating,
            'display': obj.get_rating_display()
        }

    class Meta:
        model = Comment
        fields = ('comment_id', 'rating', 'message', 'date_add', 'author', )


class TabloDetailSerializer(serializers.ModelSerializer):
    """ Одна статья блога """
    author = AuthorSerializer(read_only=True)
    comments = CommentsSerializer(many=True, read_only=True)

    class Meta:
        model = Tablo
        exclude = ('public', )  # Исключить эти поля

    def to_representation(self, instance):
        """ Переопределение вывода. Меняем формат даты в ответе """
        ret = super().to_representation(instance)
        # Конвертируем строку в дату по формату
        date_add = datetime.strptime(ret['date_add'], '%Y-%m-%dT%H:%M:%S.%f')
        # Конвертируем дату в строку в новом формате
        ret['date_add'] = date_add.strftime('%d %B %Y %H:%M:%S')
        return ret


class TabloEditorSerializer(serializers.ModelSerializer):
    """ Добавление или изменение статьи """
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Tablo
        fields = "__all__"
        read_only_fields = ['date_add', 'author', ]  # Только для чтения


class TabloMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tablo
        fields = ('id', 'title', )


class CommentAddSerializer(serializers.ModelSerializer):
    """ Добавление комментария """
    author = AuthorSerializer(read_only=True)
    note = TabloMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ['date_add', 'author', 'note']  # Только для чтения