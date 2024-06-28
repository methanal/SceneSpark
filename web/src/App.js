import React, { useState } from 'react';
import { Upload, Button, Layout, Tag, Descriptions, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import ReactPlayer from 'react-player';
import VideoClipList from './components/VideoClipList';
import { v4 as uuidv4 } from 'uuid';

const { Content, Footer, Header } = Layout;

const App = () => {
  const [videoClips, setVideoClips] = useState([]);
  const [selectedClip, setSelectedClip] = useState(null);

  const handleUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    const formData = new FormData();
    formData.append('files', file);

    const uniqueID = uuidv4();
    formData.append('request_id', uniqueID);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        const newClips = result.fileUrls.map((url, index) => ({
          url,
          tags: result.tags ? result.tags[index] : [],
          description: result.descriptions ? result.descriptions[index] : ''
        }));
        setVideoClips(prevClips => [...prevClips, ...newClips]);
        onSuccess("ok");
        message.success(`Files uploaded successfully. Request ID: ${result.request_id}`);
      } else {
        onError('上传失败');
        message.error('上传失败');
      }
    } catch (error) {
      onError(error);
      message.error('上传失败');
    }
  };

  const handleClipClick = (clip) => {
    setSelectedClip(clip);
  };

  return (
    <Layout>
      <Header>
        <Upload
          accept="video/*"
          customRequest={handleUpload}
          multiple
        >
          <Button icon={<UploadOutlined />}>Upload Video</Button>
        </Upload>
      </Header>
      <Content style={{ padding: '20px' }}>
        <VideoClipList videoClips={videoClips} onClipClick={handleClipClick} />
        {selectedClip && (
          <div style={{ marginTop: '20px' }}>
            <ReactPlayer url={selectedClip.url} controls />
            <Descriptions title="Video Clip Details" bordered>
              <Descriptions.Item label="Description">{selectedClip.description}</Descriptions.Item>
              <Descriptions.Item label="Tags">
                {selectedClip.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Video Clips App ©2024 Created by YourName
      </Footer>
    </Layout>
  );
};

export default App;
