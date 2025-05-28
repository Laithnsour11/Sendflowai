import React, { useState } from 'react';
import { Star, Send, CheckCircle, AlertCircle } from 'lucide-react';

const FeedbackModal = ({ isOpen, onClose, conversationId, onSubmit }) => {
  const [feedbackType, setFeedbackType] = useState('conversation_rating');
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [agentSelectionCorrect, setAgentSelectionCorrect] = useState(null);
  const [suggestedAgent, setSuggestedAgent] = useState('');
  const [responseEffectiveness, setResponseEffectiveness] = useState(5);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const feedbackData = {
      conversation_id: conversationId,
      feedback_type: feedbackType,
      rating: rating,
      feedback_text: feedbackText,
      agent_selection_correct: agentSelectionCorrect,
      suggested_agent: suggestedAgent,
      response_effectiveness: responseEffectiveness
    };

    try {
      await onSubmit(feedbackData);
      onClose();
      // Reset form
      setRating(0);
      setFeedbackText('');
      setAgentSelectionCorrect(null);
      setSuggestedAgent('');
      setResponseEffectiveness(5);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const StarRating = ({ value, onChange, size = 5 }) => (
    <div className="flex space-x-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          className={`${
            star <= value ? 'text-yellow-400' : 'text-gray-300'
          } hover:text-yellow-400 transition-colors`}
        >
          <Star className="h-6 w-6 fill-current" />
        </button>
      ))}
    </div>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Provide Feedback</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Feedback Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Feedback Type
            </label>
            <select
              value={feedbackType}
              onChange={(e) => setFeedbackType(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="conversation_rating">Overall Conversation Rating</option>
              <option value="agent_selection_feedback">Agent Selection Feedback</option>
              <option value="response_effectiveness">Response Effectiveness</option>
              <option value="learning_opportunity">Learning Opportunity</option>
            </select>
          </div>

          {/* Conversation Rating */}
          {feedbackType === 'conversation_rating' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How would you rate this conversation?
              </label>
              <StarRating value={rating} onChange={setRating} />
              <p className="text-sm text-gray-600 mt-1">
                {rating === 0 && "Please select a rating"}
                {rating === 1 && "Poor - Very unsatisfied"}
                {rating === 2 && "Fair - Somewhat unsatisfied"}
                {rating === 3 && "Good - Neutral"}
                {rating === 4 && "Very Good - Satisfied"}
                {rating === 5 && "Excellent - Very satisfied"}
              </p>
            </div>
          )}

          {/* Agent Selection Feedback */}
          {feedbackType === 'agent_selection_feedback' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Was the right agent selected for this conversation?
                </label>
                <div className="flex space-x-4">
                  <button
                    type="button"
                    onClick={() => setAgentSelectionCorrect(true)}
                    className={`px-4 py-2 rounded-lg border ${
                      agentSelectionCorrect === true
                        ? 'bg-green-500 text-white border-green-500'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    Yes, correct agent
                  </button>
                  <button
                    type="button"
                    onClick={() => setAgentSelectionCorrect(false)}
                    className={`px-4 py-2 rounded-lg border ${
                      agentSelectionCorrect === false
                        ? 'bg-red-500 text-white border-red-500'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    No, wrong agent
                  </button>
                </div>
              </div>

              {agentSelectionCorrect === false && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Which agent should have been used?
                  </label>
                  <select
                    value={suggestedAgent}
                    onChange={(e) => setSuggestedAgent(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a better agent</option>
                    <option value="initial_contact">Initial Contact Agent</option>
                    <option value="qualifier">Qualifier Agent</option>
                    <option value="objection_handler">Objection Handler Agent</option>
                    <option value="closer">Closer Agent</option>
                    <option value="nurturer">Nurturer Agent</option>
                    <option value="appointment_setter">Appointment Setter Agent</option>
                  </select>
                </div>
              )}
            </div>
          )}

          {/* Response Effectiveness */}
          {feedbackType === 'response_effectiveness' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How effective was the AI response at moving the conversation forward?
              </label>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">Not effective</span>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={responseEffectiveness}
                  onChange={(e) => setResponseEffectiveness(parseInt(e.target.value))}
                  className="flex-1"
                />
                <span className="text-sm text-gray-600">Very effective</span>
              </div>
              <p className="text-sm text-gray-600 mt-1 text-center">
                Rating: {responseEffectiveness}/5
              </p>
            </div>
          )}

          {/* Feedback Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Comments {feedbackType === 'learning_opportunity' ? '(Required)' : '(Optional)'}
            </label>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder={
                feedbackType === 'learning_opportunity'
                  ? "Describe what the AI could learn or do better in this situation..."
                  : "Share any additional thoughts about this interaction..."
              }
              rows={4}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              required={feedbackType === 'learning_opportunity'}
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || (feedbackType === 'conversation_rating' && rating === 0)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Submit Feedback</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const FeedbackButton = ({ conversationId, variant = 'default' }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmitFeedback = async (feedbackData) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rlhf/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      if (!response.ok) {
        throw new Error(`Feedback submission failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Feedback submitted successfully:', result);
      setSubmitted(true);
      
      // Reset submitted state after 3 seconds
      setTimeout(() => setSubmitted(false), 3000);
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  };

  const buttonClasses = {
    default: "px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors",
    small: "p-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors",
    large: "px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
  };

  if (submitted) {
    return (
      <div className="flex items-center space-x-2 text-green-600">
        <CheckCircle className="h-4 w-4" />
        <span className="text-sm">Feedback submitted!</span>
      </div>
    );
  }

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className={buttonClasses[variant] + " flex items-center space-x-2"}
      >
        <Star className="h-4 w-4" />
        <span>Feedback</span>
      </button>

      <FeedbackModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        conversationId={conversationId}
        onSubmit={handleSubmitFeedback}
      />
    </>
  );
};

export { FeedbackButton, FeedbackModal };
export default FeedbackButton;