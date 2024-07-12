import React, { useState } from 'react';
import { Button, Divider, Tabs, Descriptions, Tag } from 'antd';
import ReactPlayer from 'react-player';
import VideoClipList from './VideoClipList';

const { TabPane } = Tabs;

const VideoTabBeforeLLM = ({ videoClips4, handleFetchTab4 }) => {
  const [selectedClip4, setSelectedClip4] = useState(null);

  const handleClipClick4 = (clip) => {
    setSelectedClip4(clip);
  };

  return (
  <>
    <Tabs defaultActiveKey="1">
      <TabPane tab="Clips" key="1">
        <VideoClipList videoClips={videoClips4} onClipClick={handleClipClick4} />
        {selectedClip4 && (
          <div style={{ marginTop: '20px' }}>
            <ReactPlayer url={selectedClip4.url} controls />
            <Descriptions title="Video Clip Details" bordered>
              <Descriptions.Item label="Description">{selectedClip4.description}</Descriptions.Item>
              <Descriptions.Item label="Tags">
                {selectedClip4.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Descriptions.Item>
              <Descriptions.Item label="JSON">
                <pre>{JSON.stringify(selectedClip4, null, 2)}</pre>
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </TabPane>
    </Tabs>
  </>
  );
};

export default VideoTabBeforeLLM;
