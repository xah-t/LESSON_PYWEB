from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.db.models import Avg
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .models import Tablo, Comment
from .serializers import TablosSerializer, TabloDetailSerializer, TabloEditorSerializer

# def index(request):
#     return HttpResponse("Hello Web world!")
class TablosView(APIView):
    """ Статьи для блога """

    def get(self, request):
        """ Получить статьи для блога """
        #Это не оптимальный запрос
        notes = Tablo.objects.filter(public=True).order_by('-date_add', 'title')

       # # `select_related` - это оптимизация запроса (join). Отношение Один к Одному
       # # https://django.fun/docs/django/ru/3.1/ref/models/querysets/#select-related
       #notes = Note.objects.filter(public=True).order_by('-date_add', 'title').select_related('author')
       #
       #  # Рассчитать средний рейтинг
        notes = notes.annotate(average_rating=Avg('comments__rating'))

        serializer = TablosSerializer(notes, many=True)

        return Response(serializer.data)


class TabloDetailView(APIView):
    """ Статя блога """

    def get(self, request, note_id):
        """ Получить статю """
        # Это не оптимальный запрос
        #note = Tablo.objects.filter(pk=note_id, public=True).first()

        # # `prefetch_related` - это оптимизация запроса для отношения Многие к Одному
        # # https://django.fun/docs/django/ru/3.1/ref/models/querysets/#prefetch-related
        note = Note.objects.select_related(
            'author'
        ).prefetch_related(
            'comments'
        ).filter(
            pk=note_id, public=True
        ).first()

        if not note:
            raise NotFound(f'Опубликованная статья с id={note_id} не найдена')

        serializer = TabloDetailSerializer(note)

        return Response(serializer.data)


class TabloEditorView(APIView):
    """ Добавление или изменение статьи """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        """ Новая статья для блога """

        # Передаем в сериалайзер (валидатор) данные из запроса
        new_note = TabloEditorSerializer(data=request.data)

        # Проверка параметров
        if new_note.is_valid():
            # Записываем новую статью и добавляем текущего пользователя как автора
            new_note.save(author=request.user)
            return Response(new_note.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_note.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, note_id):

        # Находим редактируемую статью
        note = Tablo.objects.filter(pk=note_id, author=request.user).first()
        if not note:
            raise NotFound(f'Статья с id={note_id} для пользователя {request.user.username} не найдена')

        # Для сохранения изменений необходимо передать 3 параметра
        # Объект связанный со статьей в базе: `note`
        # Изменяемые данные: `data`
        # Флаг частичного оновления (т.е. можно проигнорировать обязательные поля): `partial`
        new_note = TabloEditorSerializer(note, data=request.data, partial=True)

        if new_note.is_valid():
            new_note.save()
            return Response(new_note.data, status=status.HTTP_200_OK)
        else:
            return Response(new_note.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """ Комментарий к статье """
    permission_classes = (IsAuthenticated, )

    def post(self, request, note_id):
        """ Новый комментарий """

        note = Note.objects.filter(pk=note_id).first()
        if not note:
            raise NotFound(f'Статья с id={note_id} не найдена')

        new_comment = CommentAddSerializer(data=request.data)
        if new_comment.is_valid():
            new_comment.save(note=note, author=request.user)
            return Response(new_comment.data, status=status.HTTP_201_CREATED)
        else:
            return Response(new_comment.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        """ Удалить комментарий """
        comment = Comment.objects.filter(pk=comment_id, author=request.user)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)