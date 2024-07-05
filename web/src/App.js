import React, { useState } from 'react';
import { Button, Layout, message, Upload } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { v4 as uuidv4 } from 'uuid';
import TextAreaUpload from './components/TextAreaUpload';
import VideoTabs from './components/VideoTabs';

const { Content, Footer, Header } = Layout;

const App = () => {
  const [videoClips, setVideoClips] = useState([]);
  const [videoClips2, setVideoClips2] = useState([]);
  const uniqueID = uuidv4();

  const handleUpload = async ({ file, onSuccess, onError }) => {
    const formData = new FormData();
    formData.append('files', file);
    formData.append('request_id', uniqueID);

    try {
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        onSuccess("ok");
        message.success('Files uploaded successfully');
      } else {
        onError('上传失败');
        message.error('上传失败');
      }
    } catch (error) {
      onError(error);
      message.error('上传失败');
    }
  };

  const handleFetchTab1 = async (prompt) => {
    try {
      const response = await fetch(`/api/v1/clips/extract/llm_srts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: uniqueID, prompt }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.llm_srts && result.llm_srts.length > 0) {
          setVideoClips(result.llm_srts.map(item => ({
            ...item,
            url: item.file_path,
            tags: item.tags || [],
            description: item.description || '',
          })));
          return;
        }
      } else {
        message.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Polling error:', error);
      message.error('Polling error');
    }
  };

  const handleFetchTab2 = async (prompt) => {
    try {
      const response = await fetch(`/api/v1/clips/extract/imgs_info`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ request_id: uniqueID, prompt }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.imgs_info && result.imgs_info.length > 0) {
          setVideoClips2(result.imgs_info.map(item => ({
            ...item,
            url: item.file_path,
            tags: item.tags || [],
            description: item.description || '',
          })));
          return;
        }
      } else {
        message.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Polling error:', error);
      message.error('Polling error');
    }
  };

  return (
    <Layout>
      <Header>
      </Header>
      <Content style={{ padding: '20px' }}>
        <Upload accept="video/*" customRequest={handleUpload} multiple>
          <Button icon={<UploadOutlined />}>Upload Video</Button>
        </Upload>
        <TextAreaUpload
          uniqueID={uniqueID}
          handleFetchTab1={handleFetchTab1}
          handleFetchTab2={handleFetchTab2} />
        <VideoTabs videoClips={videoClips} videoClips2={videoClips2} />
      </Content>
      <Footer style={{ textAlign: 'center' }}>
      </Footer>
    </Layout>
  );
};

export default App;
