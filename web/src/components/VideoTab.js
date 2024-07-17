import React, { useState } from 'react';
import { Button, Divider, Tabs, Descriptions, Tag } from 'antd';
import ReactPlayer from 'react-player';
import VideoClipList from './VideoClipList';

const { TabPane } = Tabs;

const VideoTab = ({ videoClips1 }) => {
  const [selectedClip1, setSelectedClip1] = useState(null);

  const handleClipClick1 = (clip) => {
    setSelectedClip1(clip);
  };

  return (
  <>
    <Tabs defaultActiveKey="1">
      <TabPane tab="Clips" key="1">
        <VideoClipList videoClips={videoClips1} onClipClick={handleClipClick1} />
        {selectedClip1 && (
          <div style={{ marginTop: '20px' }}>
            <ReactPlayer url={selectedClip1.url} controls />
            <Descriptions title="Video Clip Details" bordered>
              <Descriptions.Item label="Description">{selectedClip1.description}</Descriptions.Item>
              <Descriptions.Item label="Tags">
                {selectedClip1.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Descriptions.Item>
              <Descriptions.Item label="JSON">
                <pre>{JSON.stringify(selectedClip1, null, 2)}</pre>
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
