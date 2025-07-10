import os
import json
import base64
from typing import List
from chalice import Response, BadRequestError, NotFoundError

from chalicelib.common.constants import (
    ERR_MISSING_FIELD,
    ERR_DECODE_AUDIO,
    ERR_AUDIO_CREATE,
    ERR_AUDIO_NOT_FOUND,
    ERR_AUDIO_NOT_FOUND_QUESTION,
    ERR_AUDIO_RETRIEVE,
    ERR_AUDIO_DELETE,
    ERR_AUDIO_DOWNLOAD_S3,
    ERR_AUDIO_FILE_MISSING,
    ERR_AUDIO_DOWNLOAD,
    MSG_AUDIO_DELETED,
    ERR_CONVERSATION_NOT_FOUND,
    ERR_CONVERSATION_CREATE,
    ERR_CONVERSATION_UPDATE,
    ERR_CONVERSATION_RETRIEVE,
    ERR_CONVERSATION_DELETE,
    ERR_CONVERSATION_ACTIVE_NOT_FOUND,
    ERR_CONVERSATION_ADD_MESSAGE,
    MSG_CONVERSATION_DELETED,
    MSG_MESSAGE_ADDED,
    HEALTH_OK
)

from chalicelib.modules.models import (
    AudioResponseCreate,
    AudioResponseResponse,
    ConversationCreate,
    ConversationMessage,
    ConversationResponse,
    ConversationUpdate
)

from chalicelib.modules.srevices import AudioResponseService, ConversationService

class AudioResponseController:
    def __init__(self, app):
        self.app = app
        self.audio_service = AudioResponseService()
        self._register_routes()
    
    def _register_routes(self):
        self.app.route('/audio-responses', methods=['POST'])(self.create_audio_response)
        self.app.route('/audio-responses/{audio_id}', methods=['GET'])(self.get_audio_response)
        self.app.route('/audio-responses/candidate/{candidate_id}', methods=['GET'])(self.get_audio_responses_by_candidate)
        self.app.route('/audio-responses/candidate/{candidate_id}/question/{question_id}', methods=['GET'])(self.get_audio_response_by_question)
        self.app.route('/audio-responses/{audio_id}', methods=['DELETE'])(self.delete_audio_response)
        self.app.route('/audio-responses/{audio_id}/download', methods=['GET'])(self.download_audio_file)
        self.app.route('/audio-responses', methods=['GET'])(self.get_all_audio_responses)
        self.app.route('/health', methods=['GET'])(self.health_check)

    def create_audio_response(self):
        try:
            request_body = self.app.current_request.json_body

            required_fields = ['candidate_id', 'question_id', 'file_name', 'file_size', 'format', 'file_content']
            for field in required_fields:
                if field not in request_body:
                    raise BadRequestError(ERR_MISSING_FIELD.format(field=field))
            
            try:
                file_content = base64.b64decode(request_body['file_content'])
            except Exception as e:
                raise BadRequestError(ERR_DECODE_AUDIO.format(error=str(e)))

            audio_data = AudioResponseCreate(
                candidate_id=request_body['candidate_id'],
                question_id=request_body['question_id'],
                file_name=request_body['file_name'],
                file_size=request_body['file_size'],
                duration=request_body.get('duration'),
                format=request_body['format']
            )

            existing_response = self.audio_service.get_audio_response_by_question(
                audio_data.candidate_id, 
                audio_data.question_id
            )
            if existing_response:
                self.audio_service.delete_audio_response(str(existing_response.id))

            audio_response = self.audio_service.create_audio_response(audio_data, file_content)

            response_data = AudioResponseResponse(
                id=str(audio_response.id),
                candidate_id=audio_response.candidate_id,
                question_id=audio_response.question_id,
                file_path=audio_response.file_path,
                file_name=audio_response.file_name,
                file_size=audio_response.file_size,
                duration=audio_response.duration,
                format=audio_response.format,
                created_at=audio_response.created_at,
                updated_at=audio_response.updated_at
            )

            return Response(
                body=response_data.json(),
                status_code=201,
                headers={'Content-Type': 'application/json'}
            )
        except BadRequestError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_CREATE.format(error=str(e)))

    def get_audio_response(self, audio_id):
        try:
            audio_response = self.audio_service.get_audio_response_by_id(audio_id)
            if not audio_response:
                raise NotFoundError(ERR_AUDIO_NOT_FOUND)

            response_data = AudioResponseResponse(
                id=str(audio_response.id),
                candidate_id=audio_response.candidate_id,
                question_id=audio_response.question_id,
                file_path=audio_response.file_path,
                file_name=audio_response.file_name,
                file_size=audio_response.file_size,
                duration=audio_response.duration,
                format=audio_response.format,
                created_at=audio_response.created_at,
                updated_at=audio_response.updated_at
            )

            return response_data.json()
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_RETRIEVE.format(error=str(e)))

    def get_audio_responses_by_candidate(self, candidate_id):
        try:
            audio_responses = self.audio_service.get_audio_responses_by_candidate(candidate_id)
            responses_data = []
            for audio_response in audio_responses:
                response_data = AudioResponseResponse(
                    id=str(audio_response.id),
                    candidate_id=audio_response.candidate_id,
                    question_id=audio_response.question_id,
                    file_path=audio_response.file_path,
                    file_name=audio_response.file_name,
                    file_size=audio_response.file_size,
                    duration=audio_response.duration,
                    format=audio_response.format,
                    created_at=audio_response.created_at,
                    updated_at=audio_response.updated_at
                )
                responses_data.append(response_data.json())
            
            return {
                'count': len(responses_data),
                'audio_responses': responses_data
            }
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_RETRIEVE.format(error=str(e)))

    def get_audio_response_by_question(self, candidate_id, question_id):
        try:
            audio_response = self.audio_service.get_audio_response_by_question(candidate_id, question_id)
            if not audio_response:
                raise NotFoundError(ERR_AUDIO_NOT_FOUND_QUESTION)

            response_data = AudioResponseResponse(
                id=str(audio_response.id),
                candidate_id=audio_response.candidate_id,
                question_id=audio_response.question_id,
                file_path=audio_response.file_path,
                file_name=audio_response.file_name,
                file_size=audio_response.file_size,
                duration=audio_response.duration,
                format=audio_response.format,
                created_at=audio_response.created_at,
                updated_at=audio_response.updated_at
            )
            return response_data.json()
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_RETRIEVE.format(error=str(e)))

    def delete_audio_response(self, audio_id):
        try:
            success = self.audio_service.delete_audio_response(audio_id)
            if not success:
                raise NotFoundError(ERR_AUDIO_NOT_FOUND)
            return Response(
                body={'message': MSG_AUDIO_DELETED},
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_DELETE.format(error=str(e)))

    def download_audio_file(self, audio_id):
        try:
            audio_response = self.audio_service.get_audio_response_by_id(audio_id)
            if not audio_response:
                raise NotFoundError(ERR_AUDIO_NOT_FOUND)

            if audio_response.file_path.startswith('s3://'):
                raise BadRequestError(ERR_AUDIO_DOWNLOAD_S3)
            else:
                if not os.path.exists(audio_response.file_path):
                    raise NotFoundError(ERR_AUDIO_FILE_MISSING)

                with open(audio_response.file_path, 'rb') as f:
                    file_content = f.read()

                encoded_content = base64.b64encode(file_content).decode('utf-8')

                return Response(
                    body={
                        'file_name': audio_response.file_name,
                        'file_content': encoded_content,
                        'content_type': f'audio/{audio_response.format}'
                    },
                    status_code=200,
                    headers={'Content-Type': 'application/json'}
                )
        except (NotFoundError, BadRequestError):
            raise
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_DOWNLOAD.format(error=str(e)))

    def get_all_audio_responses(self):
        try:
            query_params = self.app.current_request.query_params or {}
            skip = int(query_params.get('skip', 0))
            limit = int(query_params.get('limit', 100))
            limit = min(limit, 100)

            audio_responses = self.audio_service.get_all_audio_responses(skip, limit)
            total_count = self.audio_service.count_audio_responses()

            responses_data = []
            for audio_response in audio_responses:
                response_data = AudioResponseResponse(
                    id=str(audio_response.id),
                    candidate_id=audio_response.candidate_id,
                    question_id=audio_response.question_id,
                    file_path=audio_response.file_path,
                    file_name=audio_response.file_name,
                    file_size=audio_response.file_size,
                    duration=audio_response.duration,
                    format=audio_response.format,
                    created_at=audio_response.created_at,
                    updated_at=audio_response.updated_at
                )
                responses_data.append(response_data.json())

            return {
                'total_count': total_count,
                'count': len(responses_data),
                'skip': skip,
                'limit': limit,
                'audio_responses': responses_data
            }
        except Exception as e:
            raise BadRequestError(ERR_AUDIO_RETRIEVE.format(error=str(e)))

    def health_check(self):
        return HEALTH_OK


class ConversationController:
    def __init__(self, app):
        self.app = app
        self.conversation_service = ConversationService()
        self._register_routes()
    
    def _register_routes(self):
        self.app.route('/conversations', methods=['POST'])(self.create_conversation)
        self.app.route('/conversations/{conversation_id}', methods=['GET'])(self.get_conversation)
        self.app.route('/conversations/{conversation_id}', methods=['PUT'])(self.update_conversation)
        self.app.route('/conversations/{conversation_id}/messages', methods=['POST'])(self.add_message)
        self.app.route('/conversations/candidate/{candidate_id}', methods=['GET'])(self.get_conversations_by_candidate)
        self.app.route('/conversations/candidate/{candidate_id}/active', methods=['GET'])(self.get_active_conversation)
        self.app.route('/conversations/{conversation_id}', methods=['DELETE'])(self.delete_conversation)

    def create_conversation(self):
        try:
            request_body = self.app.current_request.json_body
            required_fields = ['candidate_id', 'job_title', 'company_name']
            for field in required_fields:
                if field not in request_body:
                    raise BadRequestError(ERR_MISSING_FIELD.format(field=field))

            conversation_data = ConversationCreate(
                candidate_id=request_body['candidate_id'],
                job_title=request_body['job_title'],
                company_name=request_body['company_name'],
                interview_phase=request_body.get('interview_phase', 'welcome'),
                question_categories=request_body.get('question_categories', [])
            )

            conversation = self.conversation_service.create_conversation(conversation_data)

            response_data = ConversationResponse(
                id=str(conversation.id),
                candidate_id=conversation.candidate_id,
                job_title=conversation.job_title,
                company_name=conversation.company_name,
                interview_phase=conversation.interview_phase,
                current_category_index=conversation.current_category_index,
                current_question_in_category=conversation.current_question_in_category,
                messages=conversation.messages,
                question_categories=conversation.question_categories,
                interview_started=conversation.interview_started,
                interview_completed=conversation.interview_completed,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at
            )

            return Response(
                body=response_data.json(),
                status_code=201,
                headers={'Content-Type': 'application/json'}
            )
        except BadRequestError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_CREATE.format(error=str(e)))

    def get_conversation(self, conversation_id):
        try:
            conversation = self.conversation_service.get_conversation_by_id(conversation_id)
            if not conversation:
                raise NotFoundError(ERR_CONVERSATION_NOT_FOUND)

            response_data = ConversationResponse(
                id=str(conversation.id),
                candidate_id=conversation.candidate_id,
                job_title=conversation.job_title,
                company_name=conversation.company_name,
                interview_phase=conversation.interview_phase,
                current_category_index=conversation.current_category_index,
                current_question_in_category=conversation.current_question_in_category,
                messages=conversation.messages,
                question_categories=conversation.question_categories,
                interview_started=conversation.interview_started,
                interview_completed=conversation.interview_completed,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at
            )
            return response_data.json()
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_RETRIEVE.format(error=str(e)))

    def update_conversation(self, conversation_id):
        try:
            request_body = self.app.current_request.json_body
            update_data = ConversationUpdate(**request_body)

            conversation = self.conversation_service.update_conversation(conversation_id, update_data)
            if not conversation:
                raise NotFoundError(ERR_CONVERSATION_NOT_FOUND)

            response_data = ConversationResponse(
                id=str(conversation.id),
                candidate_id=conversation.candidate_id,
                job_title=conversation.job_title,
                company_name=conversation.company_name,
                interview_phase=conversation.interview_phase,
                current_category_index=conversation.current_category_index,
                current_question_in_category=conversation.current_question_in_category,
                messages=conversation.messages,
                question_categories=conversation.question_categories,
                interview_started=conversation.interview_started,
                interview_completed=conversation.interview_completed,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at
            )
            return response_data.json()
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_UPDATE.format(error=str(e)))

    def add_message(self, conversation_id):
        try:
            request_body = self.app.current_request.json_body
            message = ConversationMessage(**request_body)

            conversation = self.conversation_service.add_message_to_conversation(conversation_id, message)
            if not conversation:
                raise NotFoundError(ERR_CONVERSATION_NOT_FOUND)

            return {"message": MSG_MESSAGE_ADDED, "conversation_id": conversation_id}
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_ADD_MESSAGE.format(error=str(e)))

    def get_conversations_by_candidate(self, candidate_id):
        try:
            conversations = self.conversation_service.get_conversations_by_candidate(candidate_id)
            conversations_data = []
            for conv in conversations:
                response_data = ConversationResponse(
                    id=str(conv.id),
                    candidate_id=conv.candidate_id,
                    job_title=conv.job_title,
                    company_name=conv.company_name,
                    interview_phase=conv.interview_phase,
                    current_category_index=conv.current_category_index,
                    current_question_in_category=conv.current_question_in_category,
                    messages=conv.messages,
                    question_categories=conv.question_categories,
                    interview_started=conv.interview_started,
                    interview_completed=conv.interview_completed,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at
                )
                conversations_data.append(json.loads(response_data.json()))

            return Response(
                body=json.dumps({
                    'count': len(conversations_data),
                    'conversations': conversations_data
                }),
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_RETRIEVE.format(error=str(e)))

    def get_active_conversation(self, candidate_id):
        try:
            conversation = self.conversation_service.get_active_conversation_by_candidate(candidate_id)
            if not conversation:
                raise NotFoundError(ERR_CONVERSATION_ACTIVE_NOT_FOUND)

            response_data = ConversationResponse(
                id=str(conversation.id),
                candidate_id=conversation.candidate_id,
                job_title=conversation.job_title,
                company_name=conversation.company_name,
                interview_phase=conversation.interview_phase,
                current_category_index=conversation.current_category_index,
                current_question_in_category=conversation.current_question_in_category,
                messages=conversation.messages,
                question_categories=conversation.question_categories,
                interview_started=conversation.interview_started,
                interview_completed=conversation.interview_completed,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at
            )
            return response_data.json()
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_RETRIEVE.format(error=str(e)))

    def delete_conversation(self, conversation_id):
        try:
            success = self.conversation_service.delete_conversation(conversation_id)
            if not success:
                raise NotFoundError(ERR_CONVERSATION_NOT_FOUND)

            return Response(
                body={'message': MSG_CONVERSATION_DELETED},
                status_code=200,
                headers={'Content-Type': 'application/json'}
            )
        except NotFoundError:
            raise
        except Exception as e:
            raise BadRequestError(ERR_CONVERSATION_DELETE.format(error=str(e)))
