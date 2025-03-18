from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import QuestionBank, QuestionSetBank, PartDescription
from .serializers import QuestionBankSerializer, QuestionSetBankCreateSerializer, QuestionSetBankDetailSerializer, QuestionSetBankUpdateSerializer, QuestionSetBankListSerializer


class QuestionBankPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuestionBankListView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            search = request.GET.get('search', '')
            part_description = request.GET.get('part_description')
            difficulty_level = request.GET.get('difficulty_level')

            # Base queryset
            questions = QuestionBank.objects.all()

            # Apply filters
            if search:
                questions = questions.filter(
                    Q(question_text__icontains=search)
                )

            if part_description:
                questions = questions.filter(
                    part_description_id=part_description)

            if difficulty_level:
                questions = questions.filter(difficulty_level=difficulty_level)

            # Order by
            questions = questions.order_by('-created_at')

            # Apply pagination
            paginator = QuestionBankPagination()
            paginated_questions = paginator.paginate_queryset(
                questions, request)

            # Serialize data
            serializer = QuestionBankSerializer(paginated_questions, many=True)

            # Calculate total pages
            total_items = questions.count()
            page_size = paginator.page_size
            total_pages = (total_items + page_size - 1) // page_size

            # Get current page
            current_page = paginator.page.number if hasattr(
                paginator, 'page') else 1

            # Create response data
            response_data = {
                'results': serializer.data,
                'pagination': {
                    'total_items': total_items,
                    'total_pages': total_pages,
                    'current_page': current_page,
                    'page_size': page_size,
                    'has_next': paginator.page.has_next() if hasattr(paginator, 'page') else False,
                    'has_previous': paginator.page.has_previous() if hasattr(paginator, 'page') else False,
                    'next': paginator.get_next_link() if hasattr(paginator, 'page') else None,
                    'previous': paginator.get_previous_link() if hasattr(paginator, 'page') else None,
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionSetBankCreateView(APIView):
    def post(self, request):
        print(request.data)
        try:
            serializer = QuestionSetBankCreateSerializer(data=request.data)
            if serializer.is_valid():
                question_set = serializer.save()
                # Get the created question set with its questions
                question_set = QuestionSetBank.objects.prefetch_related(
                    'question_bank_question_set_bank'
                ).get(id=question_set.id)

                # Serialize the created question set with its questions
                response_serializer = QuestionSetBankDetailSerializer(
                    question_set)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionSetBankDetailView(APIView):
    def get(self, request, pk):
        try:
            # Get the question set with related questions
            question_set = QuestionSetBank.objects.prefetch_related(
                'question_bank_question_set_bank'
            ).get(id=pk)

            # Serialize the data
            serializer = QuestionSetBankDetailSerializer(question_set)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except QuestionSetBank.DoesNotExist:
            return Response(
                {'error': 'Question set not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionSetBankUpdateView(APIView):
    def get_object(self, pk):
        try:
            return QuestionSetBank.objects.get(pk=pk)
        except QuestionSetBank.DoesNotExist:
            return None

    def put(self, request, pk):
        question_set = self.get_object(pk)
        if question_set is None:
            return Response(
                {'error': 'Question set not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        data = request.data

        part_description = PartDescription.objects.get(id=data.get('part_description_id'))
        
        if part_description is None:
            return Response(
                {'error': 'Part description not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # update question set
        question_set.part_description = part_description
        question_set.audio = data.get('audio')
        question_set.page = data.get('page')
        question_set.image = data.get('image')
        question_set.from_ques = data.get('from_ques')
        question_set.to_ques = data.get('to_ques')
        question_set.note = data.get('note')
        question_set.save()
        
        # Get list of question IDs from request data
        question_ids = [question_data.get('id') for question_data in data.get('questions')]
        
        # Delete questions that are not in the provided list and belong to this question set
        QuestionBank.objects.filter(
            question_set=question_set
        ).exclude(
            id__in=question_ids
        ).delete()
        
        # Update existing questions or create new ones
        for question_data in data.get('questions'):
            question_id = question_data.get('id')
            if question_id:  # If ID exists, try to update existing question
                try:
                    question = QuestionBank.objects.get(id=question_id)
                    # Update existing question
                    question.question_set = question_set
                    question.part_description = part_description
                    question.question_text = question_data.get('question_text')
                    question.correct_answer = question_data.get('correct_answer')
                    question.question_number = question_data.get('question_number')
                    question.answers = question_data.get('answers')
                    question.save()
                except QuestionBank.DoesNotExist:
                    # Question with this ID doesn't exist, create a new one
                    QuestionBank.objects.create(
                        question_set=question_set,
                        part_description=part_description,
                        question_text=question_data.get('question_text'),
                        correct_answer=question_data.get('correct_answer'),
                        question_number=question_data.get('question_number'),
                        answers=question_data.get('answers')
                    )
            else:  # No ID provided, create new question
                QuestionBank.objects.create(
                    question_set=question_set,
                    part_description=part_description,
                    question_text=question_data.get('question_text'),
                    correct_answer=question_data.get('correct_answer'),
                    question_number=question_data.get('question_number'),
                    answers=question_data.get('answers')
                )
            
        # Get updated question set with related questions
        updated_question_set = QuestionSetBank.objects.prefetch_related(
            'question_bank_question_set_bank'
        ).get(id=pk)
        
        serializer = QuestionSetBankDetailSerializer(updated_question_set)

        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionSetBankPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuestionSetBankListView(APIView):
    def get(self, request):
        try:
            # Get query parameters
            # search = request.GET.get('search', '')
            part_description = request.GET.get('part_description')
            from_ques = request.GET.get('from_ques')
            to_ques = request.GET.get('to_ques')
            page = request.GET.get('page', '1')
            limit = request.GET.get('limit', '10')
            note = request.GET.get('note', '')
            
            # Convert page and limit to integers with validation
            try:
                page = int(page)
                limit = int(limit)
                # Ensure valid positive values
                page = max(1, page)
                limit = max(1, min(limit, 100))
            except (ValueError, TypeError):
                page = 1
                limit = 10

            # Base queryset
            question_sets = QuestionSetBank.objects.all()

            # Apply filters
            if note:
                question_sets = question_sets.filter(
                    Q(note__icontains=note)
                )

            if part_description:
                question_sets = question_sets.filter(
                    part_description_id=part_description)

            if from_ques:
                question_sets = question_sets.filter(from_ques__gte=from_ques)

            if to_ques:
                question_sets = question_sets.filter(to_ques__lte=to_ques)

            # Order by
            question_sets = question_sets.order_by('-created_at')
            
            # Calculate total items before pagination
            total_items = question_sets.count()
            
            # Manual pagination
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_question_sets = question_sets[start_index:end_index]

            # Serialize data
            serializer = QuestionSetBankListSerializer(
                paginated_question_sets, many=True)

            # Calculate pagination metadata
            total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
            
            # Create response data
            response_data = {
                'results': serializer.data,
                'pagination': {
                    'total_items': total_items,
                    'total_pages': total_pages,
                    'current_page': page,
                    'page_size': limit,
                    'has_next': page < total_pages,
                    'has_previous': page > 1
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionSetBankDeleteView(APIView):
    def delete(self, request, pk):
        try:
            question_set = QuestionSetBank.objects.get(id=pk)
            question_set.delete()
            return Response(
                {'message': 'Question set deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except QuestionSetBank.DoesNotExist:
            return Response(
                {'error': 'Question set not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
