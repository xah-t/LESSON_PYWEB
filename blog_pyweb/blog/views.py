from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .models import Tablo
#from .serializers import NotesSerializer, NoteDetailSerializer, NoteEditorSerializer

# def index(request):
#     return HttpResponse("Hello Web world!")
class TablosView(APIView):
    """ Статьи для блога """

    def get(self, request):
        """ Получить статьи для блога """
        notes = Tablo.objects.filter(public=True).order_by('-date_add', 'title')
        serializer = TablosSerializer(notes, many=True)

        return Response(serializer.data)


class TabloDetailView(APIView):
    """ Статя блога """

    def get(self, request, note_id):
        """ Получить статю """
        note = Tablo.objects.filter(pk=note_id, public=True).first()

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