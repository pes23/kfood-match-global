import { Box, Container, Heading, Text, VStack } from "@chakra-ui/react";
import { FoodSearchForm } from "@/components/FoodSearchForm";

export default function HomePage() {
  return (
    <Container maxW="container.lg" py={16}>
      <VStack spacing={10}>
        <Box textAlign="center">
          <Heading size="2xl" mb={4}>
            K-Food Match
          </Heading>
          <Text fontSize="l" color="gray.600">
            <br />
            좋아하는 외국 음식과 가장 비슷한 한국 음식을 찾아드립니다.
            <br />
            Find Korean dishes similar to your favorite foods.
            <br />
          </Text>

        </Box>

        <FoodSearchForm />
      </VStack>
    </Container>
  );
}
