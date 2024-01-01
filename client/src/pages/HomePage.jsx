import React, { useEffect, useState } from 'react';
import HeroSlide from '../components/common/HeroSlide';
import tmdbConfigs from "../api/configs/tmdb.configs";
import { Box } from '@mui/material';
import uiConfigs from "../configs/ui.configs";
import Container from "../components/common/Container";
import MediaItem from "../components/common/MediaItem";
import predictionApi from '../api/modules/prediction.api';
import nowplayingApi from '../api/modules/nowplaying.api';

import { SwiperSlide } from "swiper/react";
import AutoSwiper from "../components/common/AutoSwiper";
import explainApi from '../api/modules/explain.api';

const HomePage = () => {
  const [predictions, setPredictions] = useState([]);
  const [nowPlaying, setNowPlaying] = useState([]);
  const [genres, setGenres] = useState([]);

  useEffect(() => {
    const fetchPredictions = async () => {
      const { response, err } = await predictionApi.getList();

      if (response) {
        setPredictions(response);
      } else if (err) {
        console.error("Failed to fetch predictions");
      }
    };

    const fetchNowPlaying = async () => {
      const { response, err } = await nowplayingApi.getList();

      if (response) {
        setNowPlaying(response);
      } else if (err) {
        console.error("Failed to fetch now playing movies", err);
      }
    };

    const fetchExplainList = async () => {
      const { response, err } = await explainApi.getList();

      if (response) {
        const genres = response[0].explains.slice(0, 3);
        setGenres(genres);
      } else if (err) {
        console.error("Failed to fetch explain list", err);
      }
    };

    fetchPredictions();
    fetchNowPlaying();
    fetchExplainList();
  }, []);

  return (
    <>
      <HeroSlide mediaType={tmdbConfigs.mediaType.movie} mediaCategory={tmdbConfigs.mediaCategory.popular} />

      <Box marginTop="-4rem" sx={{ ...uiConfigs.style.mainContent }}>

        {genres.map((genre, i) => {
          const filteredPredictions = predictions.flatMap(prediction => prediction.predictions).filter(media => media.genre_names.includes(genre));
          return (
            filteredPredictions.length >= 5 && (
              <Container key={i} header={genre}>
                <AutoSwiper>
                  {filteredPredictions.slice(0, 10).map((media, index) => (
                    <SwiperSlide key={index}>
                      <MediaItem media={media} containerName={genre} />
                    </SwiperSlide>
                  ))}
                </AutoSwiper>
              </Container>
            )
          );
        })}

        {nowPlaying.length > 0 && (
          <Container header="Now Playing">
            <AutoSwiper>
              {nowPlaying.map((movie, index) => (
                <SwiperSlide key={index}>
                  <MediaItem media={movie} containerName="Now Playing" />
                </SwiperSlide>
              ))}
            </AutoSwiper>
          </Container>
        )}

      </Box>
    </>
  );
};

export default HomePage;
