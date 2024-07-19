import React, { useState } from 'react';
import { Button, Divider, Tabs, Descriptions, Tag } from 'antd';
import ReactPlayer from 'react-player';
import VideoClipList from './VideoClipList';

const { TabPane } = Tabs;

const VideoTab = ({ videoClips5 }) => {
  const [selectedClip5, setSelectedClip5] = useState(null);

  const handleClipClick5 = (clip) => {
    setSelectedClip5(clip);
  };

  return (
  <>
    <Tabs defaultActiveKey="1">
      <TabPane tab="Clips" key="1">
        <VideoClipList videoClips={videoClips5} onClipClick={handleClipClick5} />
        {selectedClip5 && (
          <div style={{ marginTop: '20px' }}>
            <ReactPlayer url={selectedClip5.url} controls />
            <Descriptions title="Video Clip Details" bordered>
              <Descriptions.Item label="Description">{selectedClip5.description}</Descriptions.Item>
              <Descriptions.Item label="Tags">
                {selectedClip5.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Descriptions.Item>
              <Descriptions.Item label="JSON">
                <pre>{JSON.stringify(selectedClip5, null, 2)}</pre>
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </TabPane>
    </Tabs>
  </>
  );
};

export default VideoTab;
