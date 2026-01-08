from rest_framework import serializers
from kanmind_board_app.models import Board, Task, Comment
from django.contrib.auth.models import User


class UserSerialiser(serializers.ModelSerializer):
    """
    Serializer für User-Objekte.

    Felder:
    - id: Benutzer-ID
    - email: Benutzer-E-Mail
    - fullname: Vollständiger Name oder Username, falls kein vollständiger Name gesetzt
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'fullname'
        ]
    """
    Gibt den vollständigen Namen des Users zurück. 
    Falls keiner gesetzt ist, wird der Username verwendet.
    """
    def get_fullname(self, obj):
        full_name = obj.get_full_name().strip()
        return full_name if full_name else obj.username
        

class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer für Board-Objekte (Erstellung und Listenansicht).

    Felder:
    - id, title
    - members: Liste von User-IDs (write-only)
    - owner_id: ID des Board-Eigentümers (read-only)
    - member_count: Anzahl der Mitglieder
    - ticket_count: Anzahl der Aufgaben im Board
    - tasks_to_do_count: Anzahl der Aufgaben mit Status 'to-do'
    - tasks_high_prio_count: Anzahl der Aufgaben mit Priorität 'high'

    Methoden:
    - create(): Fügt automatisch den aktuellen Benutzer zu den Board-Mitgliedern hinzu, falls nicht vorhanden
    """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    owner_id = serializers.ReadOnlyField(source='owner.id')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'members', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    """
    Erstellt ein neues Board und setzt automatisch den aktuellen Benutzer als Mitglied,
    falls er nicht bereits in der Mitgliederliste enthalten ist.
    """
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        user = self.context['request'].user

        board = Board.objects.create(
            owner=user,
            **validated_data
        )

        if user not in members:
            members.append(user)

        board.members.set(members)
        return board
    

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer für Task-Objekte (Basis).
    
    Felder:
    - board: Board-ID
    - title, description, status, priority
    - assignee_id, reviewer_id: Benutzer-IDs, optional
    - due_date
    """

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = Task
        fields = [
            'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'due_date'
        ]


class TaskSerializerWithOutBoard(TaskSerializer, serializers.ModelSerializer):
    """
    Task-Serializer ohne Board-Feld (ReadOnlyField), z.B. für Nested Serializers.
    """

    board = serializers.ReadOnlyField()
    class Meta:
            model = Task
            fields = [
                'title', 'description', 'status', 'priority',
                'assignee_id', 'reviewer_id', 'due_date'
            ]


class TaskDetailSerializer(serializers.ModelSerializer):  
    """
    Detaillierter Serializer für Task-Objekte.

    Zusätzliche Felder:
    - assignee, reviewer: Nested UserSerialiser
    - comments_count: Anzahl der Kommentare
    """

    assignee = UserSerialiser(source='assignee_id', read_only=True)
    reviewer = UserSerialiser(source='reviewer_id', read_only=True)
    comments_count = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer','due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()



class TaskDetailWithOutBoard(TaskDetailSerializer, serializers.ModelSerializer):
    """
    Task-Detail Serializer ohne Board-Feld, z.B. für Nested-Ansichten in Boards.
    """

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]



class TaskSingleSerializerPut(TaskDetailWithOutBoard):
    """
    Serializer für Task-Update (PUT), ohne Board-Feld.
    """

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date'
        ]

class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Detaillierter Serializer für Board-Objekte mit Nested Members und Tasks.
    
    Felder:
    - members: UserSerialiser
    - tasks: TaskDetailWithOutBoard
    - owner_id
    """

    members = UserSerialiser(many=True, read_only=True)
    tasks = TaskDetailWithOutBoard(many=True, read_only=True)
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner_id', 'members', 'tasks'
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer für Board-Updates (Titel + Mitglieder).

    Logik:
    - Mitglieder werden gesetzt, wenn `members` im Request enthalten ist
    """

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Board
        fields = ['title', 'members']

    """
    Aktualisiert das Board-Objekt.
    - Setzt neue Werte für Titel.
    - Aktualisiert Mitglieder, falls `members` übergeben.
    """
    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if members is not None:
            instance.members.set(members)
        return instance



class BoardResponseSerializer(serializers.ModelSerializer):
    """
    Serializer für Board-Antworten mit verschachtelten Owner- und Members-Daten.
    
    Felder:
    - owner_data: UserSerialiser
    - members_data: Liste von UserSerialiser
    """

    owner_data = UserSerialiser(source='owner', read_only=True)
    members_data = UserSerialiser(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']



class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer für Comment-Objekte.

    Felder:
    - id, content
    - author: username des Autors (read-only)
    - created_at: Datum/Zeit der Erstellung (format: ISO)
    """

    author = serializers.ReadOnlyField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']