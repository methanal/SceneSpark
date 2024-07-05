import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Input, Button, message } from 'antd';

const { TextArea } = Input;

const TextAreaUpload = ({ uniqueID, handleFetchTab1, handleFetchTab2 }) => {
  const [text1, setText1] = useState('');
  const [text2, setText2] = useState('');

  const fetchPrompts = async (uniqueID) => {
    try {
      const response = await fetch(`/api/v1/prompts/${uniqueID}`);
      if (response.ok) {
        const result = await response.json();
        setText1(result.subtitle_prompt || '');
        setText2(result.vision_prompt || '');
      } else {
        message.error('Failed to fetch prompts');
      }
    } catch (error) {
      console.error('Fetch prompts error:', error);
      message.error('Failed to fetch prompts');
    }
  };

  useEffect(() => {
    fetchPrompts(uniqueID);
  }, [uniqueID]);

  return (
    <>
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Card title="Subtitle Prompt">
            <TextArea
              value={text1}
              onChange={(e) => setText1(e.target.value)}
              placeholder="Input text here..."
              autoSize={{ minRows: 10, maxRows: 20 }}
              style={{ width: '100%' }}
            />
            <Button onClick={() => handleFetchTab1(text1)} style={{ marginTop: '16px' }}>Extract Data for Tab 1</Button>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="LLM Vision Prompt">
            <TextArea
              value={text2}
              onChange={(e) => setText2(e.target.value)}
              placeholder="Input text here..."
              autoSize={{ minRows: 10, maxRows: 20 }}
              style={{ width: '100%' }}
            />
            <Button onClick={() => handleFetchTab2(text2)} style={{ marginTop: '16px' }}>Extract Data for Tab 2</Button>
          </Card>
        </Col>
      </Row>
    </>
  );
};

export default TextAreaUpload;
